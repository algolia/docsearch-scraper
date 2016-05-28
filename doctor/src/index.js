var algoliasearch = require('algoliasearch');
var fs = require('fs');
var Slack = require('node-slackr');

var request = require('request');

var config = process.env.CONFIG;

if (config === undefined) {
    console.error("Missing CONFIG");
    process.exit(1);
}

config = JSON.parse(config);

var appId = config.appId;
var apiKey = config.apiKey;
var slackHook = config.slackHook;

var schedulerUsername = config.schedulerUsername;
var schedulerPassword = config.schedulerPassword;

var websiteUsername = config.websiteUsername;
var websitePassword = config.websitePassword;

if (schedulerUsername === undefined || schedulerPassword === undefined) {
    console.error("Missing schedulerUsername or schedulerPassword");
    process.exit(1);
}

if (websiteUsername === undefined || websitePassword === undefined) {
    console.error("Missing websiteUsername or websitePassword");
    process.exit(1);
}

if (apiKey === undefined || appId === undefined) {
    console.error("Missing appId or apiKey");
    process.exit(1);
}

if (slackHook === undefined) {
    console.error("Missing slackHook");
    process.exit(1);
}

var client = algoliasearch(appId, apiKey);

var readFile = function (path) {
    return new Promise(function (resolve, reject) {
        fs.readFile(path, function (err, data) {
            if (err) {
                data = undefined
            } else {
                data = JSON.parse(data);
            }
            resolve(data);
        });
    });
};

var fileSize = function (path) {
    return new Promise(function (resolve, reject) {
        fs.stat(path, function(err, stats) {
            var size = undefined;

            if (!err) {
                size = stats.size;
            }

            resolve(size);
        });
    });
};

var aggregateConfigs = new Promise(function (resolve, reject) {
    client.listIndexes().then(function (content) {
        var indices = content.items.filter(function (item) {
            return item.name.indexOf('_tmp') === -1;
        }).sort(function (a, b) {
            return a.name.localeCompare(b.name);
        }).map(function (item) {
            return readFile('configs/' + item.name + ".json").then(function (data) {
                resultItem = { name: item.name, config: data, noConfig: (data === undefined) }

                if (data !== undefined) {
                    resultItem.supposedNbHits = data.nb_hits || undefined;
                }
                return resultItem;
            });
        });

        return Promise.all(indices).then(function (results) {
            resolve(results);
        });
    });
});


var aggregateWithBrowse = new Promise(function (resolve, reject) {
    aggregateConfigs.then(function (indices) {
        indices = indices.map(function (elt, i) {
            return new Promise(function (resolve, reject) {
                var index = client.initIndex(elt.name);

                var browser = index.browseAll();
                var nbHits = 0;
                var allRecordsHaveH1 = true;
                var allRecordsHaveSomeContent = false;

                browser.on('result', function onResult(content) {
                    nbHits += content.hits.length;

                    content.hits.forEach(function (item) {
                        hasH1 = item.hierarchy !== undefined && item.hierarchy.h1 !== null && item.hierarchy.h1 != "";
                        hasContent = item.hierarchy !== undefined && item.hierarchy.content !== null && item.hierarchy.content != "";

                        allRecordsHaveH1 = allRecordsHaveH1 && hasH1;
                        allRecordsHaveSomeContent = allRecordsHaveSomeContent || hasContent;
                    });
                });

                browser.on('end', function onEnd() {
                    elt.nbHits = nbHits;
                    elt.allRecordsHaveH1 = nbHits == 0 || allRecordsHaveH1;
                    elt.allRecordsHaveSomeContent = nbHits == 0 || allRecordsHaveSomeContent;

                    delete(elt.config);
                    resolve(elt);
                });
            });
        });

        return Promise.all(indices).then(function (indices) {
            resolve(indices);
        });
    });
});

var aggregateWithSettings = new Promise(function (resolve, reject) {
    aggregateWithBrowse.then(function (indices) {
        indices = indices.map(function (elt, i) {
            return new Promise(function (resolve, reject) {
                var index = client.initIndex(elt.name);

                elt.anomalyInSettings = false;
                index.getSettings(function(err, content) {
                    settings = ['attributesToIndex', 'attributesToHighlight', 'attributesToRetrieve'];

                    settings.forEach(function (setting) {
                        if (content[setting] === undefined || content[setting] === null || content[setting].length <= 0) {
                            elt.anomalyInSettings = true;
                        }
                    });

                    resolve(elt);
                });
            });
        });

        return Promise.all(indices).then(function (indices) {
            resolve(indices);
        });
    });
});

var aggregateWithEmails = new Promise(function (resolve, reject) {
    aggregateWithSettings.then(function (indices) {
        indices = indices.map(function (elt, i) {
            var privatePath = 'configs_private/infos/'+ elt.name + '.txt';
            return fileSize(privatePath).then(function (size) {
                elt.noEmail = !elt.noConfig && (size === undefined || size === 0);
                return elt;
            });
        });

        return Promise.all(indices).then(function (indices) {
            resolve(indices);
        });
    });
});

var aggregateWithDuplicateCrawlers = new Promise(function (resolve, reject) {
    aggregateWithEmails.then(function (indices) {
        var url = "https://" + schedulerUsername + ":" + schedulerPassword + "@crawlers.algolia.com/1/crawlers";

        request({ url : url }, function (error, response, body) {
            crawlers = JSON.parse(body).crawlers;

            var mapping = {};

            crawlers.forEach(function (crawler) {
                if (crawler.docker_image === 'algolia/documentation-scrapper' && crawler.application_id === 'BH4D9OD16A') {
                    if (mapping[crawler.configuration.index_name] === undefined) {
                        mapping[crawler.configuration.index_name] = [];
                    }
                    mapping[crawler.configuration.index_name].push(crawler.id);
                }
            });

            var duplicates = {};

            for (var key in mapping) {
                if (mapping[key].length > 1) {
                    duplicates[key] = mapping[key];
                }
            }

            indices = indices.map(function (index) {
                index.duplicateCrawlers = false;
                index.noCrawler = false;

                crawler = crawlers.find(function (crawler) {
                    return crawler.configuration.index_name === index.name;
                });

                if (crawler) {
                    index.crawler_id = crawler.id;

                    for (var key in duplicates) {
                        if (key == index.name) {
                            index.duplicateCrawlers = true;
                            index.duplicateCrawlersList = duplicates[key];
                        }
                    }
                } else {
                    index.noCrawler = true;
                }

                return index;
            });

            resolve(indices);
        });
    });
});

var aggregateCrawlerInfo = new Promise(function (resolve, reject) {
    var url = "https://" + websiteUsername + ":" + websitePassword + "@www.algolia.com/api/1/docsearch";

    aggregateWithDuplicateCrawlers.then(function (indices) {
        request({ url : url }, function (error, response, body) {
            var connectors = JSON.parse(body).connectors;

            indices = indices.map(function (index) {
                var index_connectors = connectors.filter(function (connector) {
                    return connector.name == index.name;
                });

                index.noConnector = (index_connectors.length === 0);
                index.duplicateConnectors = (index_connectors.length > 1);

                if (!index.noConnector) {
                    index.crawler_id = index_connectors[0].crawler_id;
                }

                return index;
            });

            resolve(indices);
        });

    });
});

aggregateCrawlerInfo.then(function (indices) {
    var emptyIndices = indices.filter(function (index) {
        return index.nbHits === 0;
    });

    var indexButNoConfig = indices.filter(function (index) {
        return index.noConfig === true;
    });

    var duplicateCrawlers = indices.filter(function (index) {
        return index.duplicateCrawlers === true;
    });

    var anomalyInSettings = indices.filter(function (index) {
        return index.anomalyInSettings === true;
    });

    var noConnector = indices.filter(function (index) {
        return index.noConnector === true;
    });

    var noCrawler = indices.filter(function (index) {
        return index.noCrawler === true;
    });

    var duplicateConnectors = indices.filter(function (index) {
        return index.duplicateConnectors === true;
    });

    var potentialBadNumberOfRecords = indices.filter(function (index) {
        if (index.supposedNbHits === undefined) {
            return true;
        }

        /** Increase of 100% **/
        if (index.nbHits > 2 * index.supposedNbHits) {
            return true;
        }

        /** Decrease of 20% **/
        if (index.supposedNbHits - index.nbHits > 20 / 100 * index.supposedNbHits) {
            return true;
        }

        return false;
    });

    var configButNoEmail = indices.filter(function (index) {
        return index.noEmail === true;
    });

    var noSupposedNbHits = indices.filter(function (index) {
        return index.supposedNbHits === undefined;
    });

    var badRecords = indices.filter(function (index) {
        return index.allRecordsHaveH1 === false || index.allRecordsHaveSomeContent === false;
    });

    var reports = [];

    var sectionPrinter = function (name, list, color) {
        if (list.length > 0) {
            report = {};
            report.fallback = name;
            report.title = name;
            report.color = color;

            if (color == "danger") {
                list.push({name: "<!channel>"});
            }

            report.text = list.map(function (elt) {
                var text = '- ' + elt.name

                if (elt.name != '<!channel>') {
                    if (name === 'Indices with weird results') {
                        text += ' (got ' + elt.nbHits + ' instead of ' + elt.supposedNbHits + ')';
                    }

                    if (name === 'Duplicate crawlers') {
                        text += ' (' + elt.duplicateCrawlersList.join(', ') + ')';

                        if (elt.crawler_id !== undefined) {
                            text = text.replace(elt.crawler_id, '*' + elt.crawler_id + '*');
                        }
                    }
                }

                return text;
            }).join('\n');

            reports.push(report);
        }
    };

    sectionPrinter("Duplicate crawlers", duplicateCrawlers, "danger");
    sectionPrinter("Duplicate connector", duplicateConnectors, "warning");
    sectionPrinter("No connector found", noConnector, "warning");
    sectionPrinter("No crawler found", noConnector, "warning");
    sectionPrinter("Empty indices", emptyIndices, "danger");
    sectionPrinter("Anomaly in settings", anomalyInSettings, "danger");
    sectionPrinter("Indices without an associated config", indexButNoConfig, "warning");
    sectionPrinter("Indices with bad records", badRecords, "danger");
    sectionPrinter("Indices with weird results", potentialBadNumberOfRecords, "warning");
    sectionPrinter("Configs missing nb_hits", noSupposedNbHits, "warning");
    sectionPrinter("Configs missing email", configButNoEmail, "warning");

    if (reports.length == 0) {
        var now = new Date();
        if (now.getHours() == 10) {
            reports.push({
                color: "good",
                text: "I am alive and everything alright \\o/"
            })
        }
    }

    reports.sort(function (a, b) {
        var colors = ["danger", "warning", "good"];

        return colors.indexOf(a.color) > colors.indexOf(b.color);
    });

    var payload = {
        "text": "",
        "channel": "#docsearch-notif",
        "username": "docsearch-doctor",
        "icon_emoji": ":chart_with_upwards_trend:",
        "attachments": reports
    }

    slack = new Slack(slackHook);

    slack.notify(payload);
});