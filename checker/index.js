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


aggregateWithBrowse.then(function (indices) {
    var empty_indices = indices.filter(function (index) {
        return index.nbHits === 0;
    });

    var indexButNoConfig = indices.filter(function (index) {
        return index.noConfig === true;
    });

    var potentialBadNumberOfRecords = indices.filter(function (index) {
        return index.supposedNbHits !== undefined && Math.abs(index.nbHits - index.supposedNbHits) > (20 / 100 * index.supposedNbHits);
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

    sectionPrinter("Empty indices", empty_indices, "danger");
    sectionPrinter("Indices without an associated config", indexButNoConfig, "warning");
    sectionPrinter("Indices with bad records", badRecords, "danger");
    sectionPrinter("Indices with weird results", potentialBadNumberOfRecords, "warning");
    sectionPrinter("Config missing nb_hits", noSupposedNbHits, "warning");


    if (reports.length == 0) {
        reports.push({
            color: "good",
            text: "Everything allright \\o/"
        })
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