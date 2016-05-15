var algoliasearch = require('algoliasearch');
var fs = require('fs');
var Slack = require('node-slackr');

var config = process.env.CONFIG;

if (config === undefined) {
    console.error("Missing CONFIG");
    process.exit(1);
}

config = JSON.parse(config);

var appId = config.appId;
var apiKey = config.apiKey;
var slackHook = config.slackHook;

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


aggregateWithEmails.then(function (indices) {
    var emptyIndices = indices.filter(function (index) {
        return index.nbHits === 0;
    });

    var indexButNoConfig = indices.filter(function (index) {
        return index.noConfig === true;
    });

    var anomalyInSettings = indices.filter(function (index) {
        return index.anomalyInSettings === true;
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
                if (name === 'Indices with weird results') {
                    text += ' (got ' + elt.nbHits + ' instead of ' + elt.supposedNbHits + ')';
                }
                return text;
            }).join('\n');

            reports.push(report)
        }
    };

    sectionPrinter("Empty indices", emptyIndices, "danger");
    sectionPrinter("Anomaly in settings", anomalyInSettings, "danger");
    sectionPrinter("Indices without an associated config", indexButNoConfig, "warning");
    sectionPrinter("Indices with bad records", badRecords, "danger");
    sectionPrinter("Indices with weird results", potentialBadNumberOfRecords, "warning");
    sectionPrinter("Configs missing nb_hits", noSupposedNbHits, "warning");
    sectionPrinter("Configs missing email", configButNoEmail, "warning");

    if (reports.length == 0) {
        var now = new Date();
        if (now.getHours()) {
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
