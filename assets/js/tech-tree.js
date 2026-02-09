'use strict';

var research = ['physics', 'society', 'engineering', 'anomaly'];
var i18nData = {
    tech: {},
    category: {},
    line: {}
};

function _lineMapValue(line) {
    if (!line || !i18nData.line) {
        return line;
    }
    if (Object.prototype.hasOwnProperty.call(i18nData.line, line)) {
        return i18nData.line[line];
    }

    var compactBr = line.replace(/<br \/>/g, '<br/>');
    if (Object.prototype.hasOwnProperty.call(i18nData.line, compactBr)) {
        return i18nData.line[compactBr];
    }

    return line;
}

function _normalizeMixedLine(line) {
    if (!line || typeof line !== 'string') {
        return line;
    }

    var out = line;

    var dynamicTokenMap = {
        '[GetTechnicianSwapPluralWithIcon]': '\u00a3job_technician\u00a3\u6280\u5de5\u5c97\u4f4d',
        '[GetFarmerSwapPluralWithIcon]': '\u00a3job_farmer\u00a3\u519c\u592b\u5c97\u4f4d',
        '[GetMinerSwapPluralWithIcon]': '\u00a3job_miner\u00a3\u77ff\u5de5\u5c97\u4f4d',
        '[GetResearcherPluralWithIcon]': '\u00a3job_researcher\u00a3\u7814\u7a76\u4eba\u5458\u5c97\u4f4d',
        '[GetFoundrySwapPluralWithIcon]': '\u00a3job_foundry\u00a3\u94f8\u9020\u5c97\u4f4d',
        '[GetFactorySwapPluralWithIcon]': '\u00a3job_artisan\u00a3\u5de5\u5320\u5c97\u4f4d',
        '[technician.GetIcon]': '\u00a3job_technician\u00a3',
        '[farmer.GetIcon]': '\u00a3job_farmer\u00a3',
        '[miner.GetIcon]': '\u00a3job_miner\u00a3',
        '[foundry.GetIcon]': '\u00a3job_foundry\u00a3',
        '[GetTechnicianPlural]': '\u6280\u5de5\u5c97\u4f4d',
        '[GetFarmerPlural]': '\u519c\u592b\u5c97\u4f4d',
        '[GetMinerPlural]': '\u77ff\u5de5\u5c97\u4f4d',
        '[GetAlloyProducer]': '\u94f8\u9020\u5de5\u5c97\u4f4d',
        '[GetAlloyProducerPlural]': '\u94f8\u9020\u5de5\u5c97\u4f4d',
        '[Get技工复数形式]': '\u6280\u5de5\u5c97\u4f4d',
        '[Get农夫复数形式]': '\u519c\u592b\u5c97\u4f4d',
        '[Get矿工复数形式]': '\u77ff\u5de5\u5c97\u4f4d',
        '[Get合金Producer]': '\u94f8\u9020\u5de5\u5c97\u4f4d',
        '[Get合金Producer复数形式]': '\u94f8\u9020\u5de5\u5c97\u4f4d',
        '[Get技工Swap复数形式WithIcon]': '\u00a3job_technician\u00a3\u6280\u5de5\u5c97\u4f4d',
        '[Get农夫Swap复数形式WithIcon]': '\u00a3job_farmer\u00a3\u519c\u592b\u5c97\u4f4d',
        '[Get矿工Swap复数形式WithIcon]': '\u00a3job_miner\u00a3\u77ff\u5de5\u5c97\u4f4d',
        '[Get研究人员复数形式WithIcon]': '\u00a3job_researcher\u00a3\u7814\u7a76\u4eba\u5458\u5c97\u4f4d',
        '[Get铸造者Swap复数形式WithIcon]': '\u00a3job_foundry\u00a3\u94f8\u9020\u5c97\u4f4d',
        '[Get工厂Swap复数形式WithIcon]': '\u00a3job_artisan\u00a3\u5de5\u5320\u5c97\u4f4d'
    };
    Object.keys(dynamicTokenMap).forEach(function(key) {
        out = out.split(key).join(dynamicTokenMap[key]);
    });
    out = out.replace(/\[Get([^\]]+?)Swap复数形式WithIcon\]/g, '$1\u5c97\u4f4d');
    out = out.replace(/\[Get([^\]]+?)复数形式WithIcon\]/g, '$1\u5c97\u4f4d');
    out = out.replace(/\[Get([^\]]+?)SwapPluralWithIcon\]/g, '$1\u5c97\u4f4d');
    out = out.replace(/\[Get([^\]]+?)PluralWithIcon\]/g, '$1\u5c97\u4f4d');
    out = out.replace(/\[Get([^\]]+?)复数形式\]/g, '$1\u5c97\u4f4d');
    out = out.replace(/\[Get([^\]]+?)Plural\]/g, '$1\u5c97\u4f4d');
    out = out.replace(/\[Get[^\]]+WithIcon\]/g, '\u5c97\u4f4d');

    var resourceTokenMap = {
        '\u00a3\u80fd\u91cf\u5e01\u00a3': '\u00a3energy\u00a3',
        '\u00a3\u77ff\u7269\u00a3': '\u00a3minerals\u00a3',
        '\u00a3\u5408\u91d1\u00a3': '\u00a3alloys\u00a3'
    };
    Object.keys(resourceTokenMap).forEach(function(key) {
        out = out.split(key).join(resourceTokenMap[key]);
    });
    var regexRules = [
        [/\bHas\s+encountered\s+a\s+/gi, '遭遇过'],
        [/\bHas\s+encountered\b/gi, '遭遇过'],
        [/拥有\s+encountered\s+a\s+/g, '遭遇过'],
        [/拥有\s+encountered\b/g, '遭遇过'],
        [/\bAny\s+Country\s+Relation\b/gi, '任意帝国关系'],
        [/\bHas\s+communication\s+with\s+our\s+Empire\b/gi, '已与我国建立通讯'],
        [/\bHas\s+communication\s+with\s+our\s+帝国\b/g, '已与我国建立通讯'],
        [/\bHas\s+communication\s+与我国\b/g, '已与我国建立通讯'],
        [/\bHas\s+与我国建立通讯\b/g, '已与我国建立通讯'],
        [/\bcommunication\s+with\s+our\s+Empire\b/gi, '与我国建立通讯'],
        [/\bcommunication\s+with\s+our\s+帝国\b/g, '与我国建立通讯'],
        [/拥有\s+communication\s+with\s+our\s+Empire/g, '已与我国建立通讯'],
        [/拥有\s+communication\s+与我国/g, '已与我国建立通讯'],
        [/拥有\s+与我国建立通讯/g, '已与我国建立通讯'],
        [/\bcommunication\s+与我国\b/g, '与我国建立通讯'],
        [/\bControls\s+a\s+system\s+with\s+a\s+Gateway\b/gi, '控制有星门的星系'],
        [/\bControls\s+a\s+system\s+with\s+a\s+bypass_lgate\b/gi, '控制有L-星门的星系'],
        [/\bControls\s+a\s+system\s+with\s+a\s+Natural\s+Wormhole\b/gi, '控制有天然虫洞的星系'],
        [/控制\s+a\s+system\s+with\s+a\s+Gateway/g, '控制有星门的星系'],
        [/控制\s+a\s+system\s+with\s+a\s+星门/g, '控制有星门的星系'],
        [/控制\s+a\s+system\s+with\s+a\s+bypass_lgate/g, '控制有L-星门的星系'],
        [/控制\s+a\s+system\s+with\s+a\s+Natural\s+Wormhole/g, '控制有天然虫洞的星系'],
        [/控制\s+a\s+system\s+with\s+a\s+天然虫洞/g, '控制有天然虫洞的星系'],
        [/\bencountered\s+is\s+lower\s+than\b/gi, '遭遇次数小于'],
        [/\bencountered\s+is\s+greater\s+than\b/gi, '遭遇次数大于'],
        [/\bis\s+greater\s+than\s+or\s+equal\s+to\b/gi, '大于等于'],
        [/\bis\s+lower\s+than\s+or\s+equal\s+to\b/gi, '小于等于'],
        [/\bis\s+greater\s+than\b/gi, '大于'],
        [/\bis\s+lower\s+than\b/gi, '小于'],
        [/\bis\s+equal\s+to\b/gi, '等于'],
        [/\bis\s+not\s+equal\s+to\b/gi, '不等于']
    ];
    regexRules.forEach(function(rule) {
        out = out.replace(rule[0], rule[1]);
    });

    var textRules = [
        ['bypass_lgate', 'L-星门'],
        ['bypass_relay_bypass', '中继器通道'],
        ['default', '常规帝国'],
        ['with our 帝国', '与我国'],
        ['our Empire', '我国']
    ];
    textRules.forEach(function(rule) {
        out = out.split(rule[0]).join(rule[1]);
    });

    out = out.replace(/\bEnergy\s+Credits\s+from\b/gi, '\u80fd\u91cf\u5e01\u4ea7\u81ea');
    out = out.replace(/\bMinerals\s+from\b/gi, '\u77ff\u7269\u4ea7\u81ea');
    out = out.replace(/\bFood\s+from\b/gi, '\u98df\u7269\u4ea7\u81ea');
    out = out.replace(/\bTrade\s+from\b/gi, '\u8d38\u6613\u4ea7\u81ea');
    out = out.replace(/\bResources\s+from\b/gi, '\u8d44\u6e90\u4ea7\u81ea');
    out = out.replace(/\bfrom\s+\u00a3job\u00a3\s*Jobs\b/gi, '\u6765\u81ea\u00a3job\u00a3\u5c97\u4f4d');
    out = out.replace(/\bfrom\s+\u00a3job\u00a3\s*jobs\b/gi, '\u6765\u81ea\u00a3job\u00a3\u5c97\u4f4d');
    out = out.replace(/\u80fd\u91cf\u5e01\s+from/g, '\u80fd\u91cf\u5e01\u4ea7\u81ea');
    out = out.replace(/\u77ff\u7269\s+from/g, '\u77ff\u7269\u4ea7\u81ea');
    out = out.replace(/\u98df\u7269\s+from/g, '\u98df\u7269\u4ea7\u81ea');
    out = out.replace(/\u8d38\u6613\s+from/g, '\u8d38\u6613\u4ea7\u81ea');
    out = out.replace(/\u4ea7\u81ea\s+\u00a3job\u00a3\s*Jobs/g, '\u6765\u81ea\u00a3job\u00a3\u5c97\u4f4d');
    out = out.replace(/\u6765\u81ea\u00a3job\u00a3\s*Jobs/g, '\u6765\u81ea\u00a3job\u00a3\u5c97\u4f4d');

    return out;
}

function _translateLines(lines, dedupe) {
    if (!Array.isArray(lines) || lines.length === 0) {
        return lines;
    }

    var translated = lines.map(function(line) {
        return _normalizeMixedLine(_lineMapValue(line));
    });

    if (!dedupe) {
        return translated;
    }

    var seen = new Set();
    return translated.filter(function(line) {
        if (seen.has(line)) {
            return false;
        }
        seen.add(line);
        return true;
    });
}

function _applyNodeI18n(tech) {
    if (!tech || typeof tech !== 'object') {
        return;
    }

    var techMap = i18nData.tech || {};
    var categoryMap = i18nData.category || {};
    var techI18n = tech.key ? techMap[tech.key] : null;

    if (techI18n) {
        if (techI18n.name) {
            tech.name = techI18n.name;
        }
        if (techI18n.description) {
            tech.description = techI18n.description;
        }
    }

    if (tech.category && Object.prototype.hasOwnProperty.call(categoryMap, tech.category)) {
        tech.category = categoryMap[tech.category];
    }

    if (Array.isArray(tech.weight_modifiers)) {
        tech.weight_modifiers = _translateLines(tech.weight_modifiers, false);
    }
    if (Array.isArray(tech.potential)) {
        tech.potential = _translateLines(tech.potential, false);
    }
    if (Array.isArray(tech.feature_unlocks)) {
        tech.feature_unlocks = _translateLines(tech.feature_unlocks, true);
    }
    if (Array.isArray(tech.prerequisites_names)) {
        tech.prerequisites_names = tech.prerequisites_names.map(function(prerequisite) {
            if (!prerequisite || !prerequisite.key) {
                return prerequisite;
            }
            var translated = techMap[prerequisite.key];
            if (translated && translated.name) {
                return Object.assign({}, prerequisite, { name: translated.name });
            }
            return prerequisite;
        });
    }
}

function load_i18n() {
    return $.getJSON('i18n.zh-hans.json')
        .done(function(jsonData) {
            i18nData = {
                tech: jsonData.tech || {},
                category: jsonData.category || {},
                line: jsonData.line || {}
            };
            console.log('Loaded i18n.zh-hans.json');
        })
        .fail(function() {
            i18nData = { tech: {}, category: {}, line: {} };
            console.log('No i18n.zh-hans.json found for current version');
        });
}

var config = {
    //container: '#tech-tree-',
    rootOrientation: 'WEST', // NORTH || EAST || WEST || SOUTH
    nodeAlign: 'TOP',
    hideRootNode: true,
    siblingSeparation: 20,
    subTeeSeparation:  20,
    scrollbar: 'resize',
    connectors: {
        type: 'step'
    },
    node: {
        HTMLclass: 'tech',
        collapsable: false
    },
    callback: {
        onTreeLoaded: function(tree) {
            init_tooltips();

            var area = tree.nodeHTMLclass.replace('tech', '').replace(' ', '');
            init_nodestatus(area);

            const observer = lozad();
            observer.observe();
		}
    }
};

function init_tooltips() {

    $('.node:not(.tooltipstered)').tooltipster({
        minWidth: 300,
        trigger: 'click',
        maxWidth: 512,
        functionInit: function(instance, helper){
            var content = $(helper.origin).find('.extra-data');
            $(content).find('img').each(function(img, el) {
                $(el).attr('src',$(el).attr('data-src'));
                
                var tech = $(el)[0].classList[$(el)[0].classList.length-1];
                if(!$('#' + tech).hasClass('anomaly')) {
                    var parent = $('#' + tech)[0];
                    if(parent !== undefined && parent.classList.length > 1)
                    $(el).addClass(parent.classList[2]);
                }
            });
            instance.content($('<div class="ui-tooltip">' + $(content).html() + '</div>'));
        },
        functionReady: function(instance, helper) {
            $(helper.tooltip).find('.tooltip-content').each(function(div){
                var content = $(this).html();
                content = content.replace(new RegExp(/£(\w+)£/,'g'), '<img class="resource" src="../assets/icons/$1.png" />');
                $(this).html(content);
            });
            $(helper.tooltip).find('.node-status').each(function() {
                var tech = $(this)[0].classList[1];
                if($('#' + tech).find('div.node-status').hasClass('active')) {
                    $(this).addClass('active');
                } else {
                    $(this).removeClass('active');
                }
            });
        }
    });
}

function setup(tech) {
    _applyNodeI18n(tech);

    var techClass = (tech.is_dangerous ? ' dangerous' : '')
        + (!tech.is_dangerous && tech.is_rare ? ' rare' : '');

    var tmpl = $.templates("#node-template");
    var html = tmpl.render(tech);

    tech.HTMLid = tech.key;
    tech.HTMLclass = tech.area + techClass + (tech.is_start_tech ? ' active' : '');

    var output = html;
    if(tech.is_start_tech) {
        var e = $('<div>' + html + '</div>');
        e.find('div.node-status').addClass('active').addClass('status-loaded');
        output = e.html();
    }

    tech.innerHTML = output;

    $(tech.children).each(function(i, node) {
        setup(node);
    });
};

function setup_search() {
    const trees = document.querySelector('#tech-tree').querySelectorAll("[id|='tech-tree']");

    let nodes = Array.from(trees).filter((t) => {
        return t.getAttribute("class") == null || !t.getAttribute("class").includes("float-NoDisplay");
    }).reduce((a, b) => { a.push(...b.querySelectorAll('.node.tech')); return a; }, []);
    nodes = nodes.reduce((a, b) =>  {
        let the_text = '';
        b.querySelectorAll('.node-name, .extra-data .tooltip-content:not(.prerequisites)').forEach(data => {
            the_text += data.innerText;
            the_text += data.title;
        });
        a.push({ node: b, text: the_text });
        return a;
    }, []);

    const debounce = (callback, wait) => {
        let timeoutId = null;
        return (...args) => {
            window.clearTimeout(timeoutId);
            timeoutId = window.setTimeout(() => {
                callback.apply(null, args);
            }, wait);
        };
    };

    let current_idx = 0;
    current_idx = 0;
    let last_search_term = "";
    $("#deepsearch").on("change keyup paste", debounce(function () {
        const search_term = $('#deepsearch').val();
        if (search_term == last_search_term) {
            return;
        } else {
            last_search_term = search_term;
        }

        current_idx = 0;
        if (!search_term) {
            nodes.forEach(n => n.node.style.opacity = 1);
            return;
        }
        
        let hits = nodes.filter(n => {
            const match = n.text.toLowerCase().includes(search_term.toLowerCase());
            
            n.node.style.opacity = match ? 0.6 : 0.1;

            return match;
        });

        console.log(hits.length);


        hits.sort((a, b) => {
            return a.node.getBoundingClientRect().top - b.node.getBoundingClientRect().top || a.node.getBoundingClientRect().left - b.node.getBoundingClientRect().left;
        });

        let first_hit = true;

        hits.forEach(n => {
            if (first_hit) {
                first_hit = false;
                console.log(n.node);
                n.node.scrollIntoView({
                    behavior: "smooth",
                    block: "center",
                    inline: "nearest",
                  });
                n.node.style.opacity = 1;
            } else {
                n.node.style.opacity = 0.6;
            }
        })

    }, 300));

    $("#deepsearch").on('keypress',function(e) {
        if(e.which == 13) {
            const search_term = $('#deepsearch').val();

            let hits = nodes.filter(n => {
                const match = n.text.toLowerCase().includes(search_term.toLowerCase());
                
                n.node.style.opacity = match ? 0.6 : 0.1;
    
                return match;
            });
    
    
            hits.sort((a, b) => {
                return a.node.getBoundingClientRect().top - b.node.getBoundingClientRect().top || a.node.getBoundingClientRect().left - b.node.getBoundingClientRect().left;
            });

            if (hits.length == 0) {
                return; 
            }

            hits[current_idx % hits.length].node.style.opacity = 0.6;
            let current_focused = hits[(current_idx + 1) % hits.length].node;
            current_focused.scrollIntoView({
                behavior: "smooth",
                block: "center",
                inline: "nearest",
              });
            current_focused.style.opacity = 1;

            current_idx += 1;
        }
    });
};


$(document).ready(function() {
    load_i18n().always(function() {
        load_tree();

        let checkExist = setInterval(() => {
            if (document.querySelector('#tech-tree')) {
               clearInterval(checkExist);
               setup_search();
            };
        }, 100);
    });
});

function _load(jsonData, tree) {
    var container = '#tech-tree-' + jsonData.children[0].name;
    var myconfig = {container: container};
    $.extend(true, myconfig, config);

    charts[tree] = new Treant({chart:myconfig, nodeStructure: jsonData.children[0]}, function () {},$);
}

function load_tree() {
    research.forEach( area => {
        if('anomaly' !== area) {
            $.getJSON( area + '.json', function(jsonData) {
                setup(jsonData);
                _load(jsonData, area);
            });
        }
    });
    $.getJSON('anomalies.json', function(jsonData) {
        // Event techs don't really need a Tree
        $(jsonData).each(function(index, item) {
            setup(item);
            var e = $("<div>").html(item.innerHTML);
            e.attr("id", item.key);
            e.attr("class",item.HTMLclass)
            e.addClass("node").addClass("tech").addClass("anomaly");
            $('#tech-tree-anomalies').append(e);
        });
        init_nodestatus('anomalies');
        init_tooltips();
    });
    if(window.indexedDB) {
        initDB();
    }
    else if (window.localStorage) {
        setupLocalStorage();
    }
}
