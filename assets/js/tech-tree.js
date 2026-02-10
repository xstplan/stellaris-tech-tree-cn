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
        '[GetArtisanIcon]': '\u00a3job_artisan\u00a3',
        '[GetArtisan]': '\u5de5\u5320',
        '[GetSpecialist]': '\u4e13\u5bb6',
        '[GetWorker]': '\u52b3\u5de5',
        '[GetCrimeDeviancy]': '\u72af\u7f6a\u5ea6/\u53cd\u5e38\u5ea6',
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
    out = out.replace(/\[Get([^\]]+?)Icon\]\s*/g, '');
    out = out.replace(/\[Get([^\]]+?)\]/g, '$1');
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
        [/\bBuild\s+Cost\b/gi, '\u5efa\u9020\u82b1\u8d39'],
        [/\bThe\s+Empire\s+Size\s+Effect\s+is\s+modified\s+by\b/gi, '\u5e1d\u56fd\u89c4\u6a21\u6548\u5e94\u4fee\u6b63\u4e3a'],
        [/\bCan\s+research\s+technology\b/gi, '\u53ef\u7814\u7a76\u79d1\u6280'],
        [/\bAI\s+Personality\b/gi, 'AI\u6027\u683c'],
        [/\bCrisis\s+level\b/gi, '\u5371\u673a\u7b49\u7ea7'],
        [/\bIs\s+a\s+Member\s+of\s+a\s+spiritualist\s+Federation\s+with\s+perk\s+'A\s+Union\s+of\s+Faith'\b/gi, '\u662f\u62e5\u6709\u201c\u4fe1\u4ef0\u540c\u76df\u201d\u7279\u5178\u7684\u552f\u5fc3\u4e3b\u4e49\u8054\u90a6\u6210\u5458'],
        [/\bASTRAL_RIFT\b/gi, '\u661f\u754c\u88c2\u9699'],
        [/\bastral\s+scar\b/gi, '\u661f\u754c\u88c2\u75d5'],
        [/\bSpecies\s+Leader\s+Exp\s+Gain\b/gi, '\u7269\u79cd\u9886\u8896\u7ecf\u9a8c\u83b7\u53d6'],
        [/\bEmpire\s+Size\s+from\s+Pops\b/gi, '\u4eba\u53e3\u5bfc\u81f4\u7684\u5e1d\u56fd\u89c4\u6a21'],
        [/\bUrban\s+District\s+Housing\b/gi, '\u90fd\u5e02\u533a\u5212\u4f4f\u623f'],
        [/\bPop\s+Resource\s+Output\b/gi, '\u4eba\u53e3\u8d44\u6e90\u4ea7\u51fa'],
        [/\bJob\s+Efficiency\b/gi, '\u5c97\u4f4d\u6548\u7387'],
        [/\bMajor\s+Capital\s+Buildings\b/gi, '\u4e3b\u90fd\u5efa\u7b51'],
        [/\bUpgraded\s+Capital\s+Buildings\b/gi, '\u5347\u7ea7\u9996\u90fd\u5efa\u7b51'],
        [/\bCapital\s+Buildings\b/gi, '\u9996\u90fd\u5efa\u7b51'],
        [/\bMind\s+over\s+Matter\b/gi, '\u8d85\u51e1\u5165\u5723'],
        [/\bTeachers\s+of\s+the\s+Shroud\b/gi, '\u865a\u5883\u5bfc\u5e08'],
        [/\bGenome\s+Mapping\b/gi, '\u57fa\u56e0\u6d4b\u7ed8'],
        [/\bHas\s+DLC\s+Astral\s+Planes\b/gi, '\u62e5\u6709 DLC \u661f\u754c\u4f4d\u9762'],
        [/\bHas\s+DLC\s+Biogenesis\b/gi, '\u62e5\u6709 DLC \u751f\u4f53\u8fdb\u5316'],
        [/\bHas\s+DLC\s+Megacorp\b/gi, '\u62e5\u6709 DLC \u5de8\u578b\u4f01\u4e1a'],
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
        [/\bNumber\s+of\s+years\s+since\s+game\s+start\b/gi, '开局后年数'],
        [/\byears\s+since\s+game\s+start\b/gi, '开局后年数'],
        [/数量\s+years\s+since\s+game\s+start\b/g, '开局后年数'],
        [/\bNumber\s+of\b/gi, '数量'],
        [/\bPop\s+count\b/gi, '人口数量'],
        [/\blevel\b/gi, '等级'],
        [/\bin\s+nebula\b/gi, '位于星云中'],
        [/\barchetype\b/gi, '原型'],
        [/\bcommunications\b/gi, '通讯'],
        [/\ba\s+number\s+of\s+pop\b/gi, '人口数量'],
        [/\bexists\b/gi, '存在'],
        [/\bsubject\b/gi, '附属国'],
        [/\bwithin\s+borders\b/gi, '境内'],
        [/\bin\s+construction\b/gi, '在建造中'],
        [/\bdisabled\b/gi, '已禁用'],
        [/\bopen\s+ascension\s+perk\s+slots\b/gi, '可用飞升天赋槽位'],
        [/\bCountry\s+does\s+NOT\s+use\s+biological\s+ships\b/gi, '国家不使用生物舰船'],
        [/\bCountry\s+uses\s+biological\s+ships\b/gi, '国家使用生物舰船'],
        [/\ba\s+bulwark\s+\(specialised\s+subject\)/gi, '堡垒子国'],
        [/\ba\s+prospectorium\s+\(specialised\s+subject\)/gi, '勘探子国'],
        [/\ba\s+scholarium\s+\(specialised\s+subject\)/gi, '学者子国'],
        [/\bLaw\s+None\b/gi, '法律：无'],
        [/\bLarge\b/gi, '大型'],
        [/\bMedium\b/gi, '中型'],
        [/\bSmall\b/gi, '小型'],
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
        ['Blue Eye Beam', '\u84dd\u8272\u773c\u5149\u675f'],
        ['Gamma Eye Beam', '\u4f3d\u9a6c\u773c\u5149\u675f'],
        ['UV Eye Beam', '\u7d2b\u5916\u773c\u5149\u675f'],
        ['X-Ray Eye Beam', 'X\u5c04\u7ebf\u773c\u5149\u675f'],
        ['Orbital Growth Chamber', '\u8f68\u9053\u751f\u957f\u8231'],
        ['Calamity', '\u707e\u5384'],
        ['Danger', '\u5371\u9669'],
        ['Existential Threat', '\u751f\u5b58\u5a01\u80c1'],
        ['Risk', '\u98ce\u9669'],
        ['Cuthuloids', '\u514b\u82cf\u9c81\u4f53'],
        ['Arc Furnace', '\u7535\u5f27\u7194\u7089'],
        ['Borehole Pumps', '\u94bb\u5b54\u6cf5'],
        ['Equatorial Band', '\u8d64\u9053\u5e26'],
        ['Mohole Extractors', '\u83ab\u970d\u5f00\u91c7\u673a'],
        ['Dyson Swarm: Constellation', '\u6234\u68ee\u8702\u7fa4\uff1a\u661f\u7fa4'],
        ['Dyson Swarm: Array', '\u6234\u68ee\u8702\u7fa4\uff1a\u9635\u5217'],
        ['Mega Shipyard Core', '\u5de8\u578b\u8239\u575e\u6838\u5fc3'],
        ['Mega Shipyard Framework', '\u5de8\u578b\u8239\u575e\u6846\u67b6'],
        ['Mega Shipyard Site', '\u5de8\u578b\u8239\u575e\u5de5\u5730'],
        ['Quantum Catapult Single Array', '\u91cf\u5b50\u5f39\u5f13\u5355\u9635\u5217'],
        ['Quantum Catapult Twin Arrays', '\u91cf\u5b50\u5f39\u5f13\u53cc\u9635\u5217'],
        ['Quantum Catapult Site', '\u91cf\u5b50\u5f39\u5f13\u5de5\u5730'],
        ['Strategic Coordination Center Site', '\u6218\u7565\u534f\u8c03\u4e2d\u5fc3\u5de5\u5730'],
        ['Matter Decompressor Site', '\u7269\u8d28\u89e3\u538b\u5668\u5de5\u5730'],
        ['Grand Archive', '\u535a\u7269\u5929\u67a2'],
        ['Megastructure', '\u5de8\u578b\u7ed3\u6784'],
        ['Single', '\u5355'],
        ['Twin', '\u53cc'],
        ['Ruined', '\u635f\u6bc1'],
        ['Accelerated Juvenile Growth Gland', '\u52a0\u901f\u5e7c\u4f53\u751f\u957f\u817a\u4f53'],
        ['Juvenile Growth Gland', '\u5e7c\u4f53\u751f\u957f\u817a\u4f53'],
        ['Mature Growth Gland', '\u6210\u719f\u751f\u957f\u817a\u4f53'],
        ['Ancient Energised Carapace', '\u8fdc\u53e4\u5145\u80fd\u7532\u58f3'],
        ['Autonomous Ship Intellect', '\u81ea\u4e3b\u8230\u8239\u667a\u80fd'],
        ['Bio-Swarmer Missiles', '\u751f\u7269\u8702\u7fa4\u5bfc\u5f39'],
        ['Bio-Whirlwind Missiles', '\u751f\u7269\u65cb\u98ce\u5bfc\u5f39'],
        ['Improved Rangefinder Cluster', '\u6539\u826f\u6d4b\u8ddd\u96c6\u7fa4'],
        ['Rapid Incubation Matrix', '\u5feb\u901f\u5b75\u5316\u77e9\u9635'],
        ['Large Nanite Quill Battery', '\u5927\u578b\u7eb3\u7c73\u68d8\u523a\u70ae\u7ec4'],
        ['Medium Nanite Quill Battery', '\u4e2d\u578b\u7eb3\u7c73\u68d8\u523a\u70ae\u7ec4'],
        ['Small Nanite Quill Battery', '\u5c0f\u578b\u7eb3\u7c73\u68d8\u523a\u70ae\u7ec4'],
        ['Large Ripper Quill Battery', '\u5927\u578b\u6495\u88c2\u68d8\u523a\u70ae\u7ec4'],
        ['Medium Ripper Quill Battery', '\u4e2d\u578b\u6495\u88c2\u68d8\u523a\u70ae\u7ec4'],
        ['Small Ripper Quill Battery', '\u5c0f\u578b\u6495\u88c2\u68d8\u523a\u70ae\u7ec4'],
        ['Large Stormfire Quill Battery', '\u5927\u578b\u98ce\u66b4\u706b\u68d8\u523a\u70ae\u7ec4'],
        ['Medium Stormfire Quill Battery', '\u4e2d\u578b\u98ce\u66b4\u706b\u68d8\u523a\u70ae\u7ec4'],
        ['Small Stormfire Quill Battery', '\u5c0f\u578b\u98ce\u66b4\u706b\u68d8\u523a\u70ae\u7ec4'],
        ['Advanced Combat Computer', '\u5148\u8fdb\u4f5c\u6218\u7535\u8111'],
        ['Sapient Combat Computer', '\u667a\u6167\u578b\u4f5c\u6218\u7535\u8111'],
        ['Combat Computer', '\u4f5c\u6218\u7535\u8111'],
        ['Bio-Hyperlane Field III', '\u751f\u7269\u8d85\u7a7a\u95f4\u822a\u9053\u573a III'],
        ['Hyper Drive III', '\u8d85\u7a7a\u95f4\u5f15\u64ce III'],
        ['NEUROCHIPS', '\u795e\u7ecf\u82af\u7247'],
        ['Large Red Beam Projector', '大型红色光束投射器'],
        ['Medium Red Beam Projector', '中型红色光束投射器'],
        ['Small Red Beam Projector', '小型红色光束投射器'],
        ['Large Blue Beam Projector', '大型蓝色光束投射器'],
        ['Medium Blue Beam Projector', '中型蓝色光束投射器'],
        ['Small Blue Beam Projector', '小型蓝色光束投射器'],
        ['Large Gamma Beam Projector', '大型伽马光束投射器'],
        ['Medium Gamma Beam Projector', '中型伽马光束投射器'],
        ['Small Gamma Beam Projector', '小型伽马光束投射器'],
        ['Large X-Ray Beam Projector', '大型X射线光束投射器'],
        ['Medium X-Ray Beam Projector', '中型X射线光束投射器'],
        ['Small X-Ray Beam Projector', '小型X射线光束投射器'],
        ['Large UV Beam Projector', '大型紫外光束投射器'],
        ['Medium UV Beam Projector', '中型紫外光束投射器'],
        ['Small UV Beam Projector', '小型紫外光束投射器'],
        ['Large Bio-Plasma Accelerator', '大型生物等离子加速炮'],
        ['Medium Bio-Plasma Accelerator', '中型生物等离子加速炮'],
        ['Small Bio-Plasma Accelerator', '小型生物等离子加速炮'],
        ['Large Bio-Plasma Cannon', '大型生物等离子加农炮'],
        ['Medium Bio-Plasma Cannon', '中型生物等离子加农炮'],
        ['Small Bio-Plasma Cannon', '小型生物等离子加农炮'],
        ['Large Bio-Plasma Thrower', '大型生物等离子喷射炮'],
        ['Medium Bio-Plasma Thrower', '中型生物等离子喷射炮'],
        ['Small Bio-Plasma Thrower', '小型生物等离子喷射炮'],
        ['Starbase', '恒星基地'],
        ['Module', '模块'],
        ['Upgrade', '升级'],
        ['Country', '国家'],
        ['Perk', '特典'],
        ['Array', '阵列'],
        ['Arrays', '阵列'],
        ['Site', '站点'],
        ['Battery', '电池'],
        ['Capacity', '容量'],
        ['Offspring', '后代'],
        ['Quill', '棘刺'],
        ['Sapient', '智慧'],
        ['Nanite', '纳米'],
        ['Ripper', '撕裂'],
        ['Stormfire', '风暴火'],
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
    out = out.replace(/([\u4e00-\u9fff])s\b/g, '$1');
    out = out.replace(/\u6570\u91cf of /g, '\u6570\u91cf');
    out = out.replace(/\u56fd\u5bb6 uses /g, '\u56fd\u5bb6\u4f7f\u7528');
    out = out.replace(/\u751f\u7269 ships/g, '\u751f\u7269\u8230\u8239');
    out = out.replace(/playable \u5e1d\u56fd met/g, '\u53ef\u6e38\u73a9\u5e1d\u56fd\u5df2\u63a5\u89e6\u6570\u91cf');
    out = out.replace(/Percentage of /g, '');
    out = out.replace(/the completed_/g, '\u5df2\u5b8c\u6210_');
    out = out.replace(/ completed /g, ' \u5df2\u5b8c\u6210 ');
    out = out.replace(/Mind over \u7269\u8d28/g, '\u8d85\u51e1\u5165\u5723');
    out = out.replace(/Feature: /g, '\u7279\u6027\uff1a');
    out = out.replace(/Output /g, '\u4ea7\u51fa ');
    out = out.replace(/\u84dd\u773c\u5149\u7ebf/g, '\u84dd\u8272\u773c\u5149\u675f');
    out = out.replace(/\u4f3d\u9a6c\u773c\u5149\u7ebf/g, '\u4f3d\u9a6c\u773c\u5149\u675f');
    out = out.replace(/\u7d2b\u5916\u773c\u5149\u7ebf/g, '\u7d2b\u5916\u773c\u5149\u675f');
    out = out.replace(/X\u5c04\u7ebf\u773c\u5149\u7ebf/g, 'X\u5c04\u7ebf\u773c\u5149\u675f');
    out = out.replace(/\u5e1d\u56fd\u89c4\u6a21 from Pops/g, '\u4eba\u53e3\u5bfc\u81f4\u7684\u5e1d\u56fd\u89c4\u6a21');
    out = out.replace(/Urban \u533a\u5212 \u4f4f\u623f/g, '\u90fd\u5e02\u533a\u5212\u4f4f\u623f');
    out = out.replace(/\u7269\u79cd \u9886\u8896 Exp Gain/g, '\u7269\u79cd\u9886\u8896\u7ecf\u9a8c\u83b7\u53d6');
    out = out.replace(/\u72af\u7f6a\u5ea6\u53cd\u5e38\u5ea6/g, '\u72af\u7f6a\u5ea6/\u53cd\u5e38\u5ea6');
    out = out.replace(/\u5de5\u866b\u4eba\u53e3\u8d44\u6e90\u4ea7\u51fa/g, '\u52b3\u5de5\u4eba\u53e3\u8d44\u6e90\u4ea7\u51fa');
    out = out.replace(/\u963f\u65af\u7279\u62c9l Planes/g, '\u661f\u754c\u4f4d\u9762');
    out = out.replace(/DLC \u8fdc\u53e4 \u9057\u73cd Story Pack/g, 'DLC \u8fdc\u53e4\u9057\u7269\u6545\u4e8b\u5305');
    out = out.replace(/\u00a3\u8f7b\u5ea6_artifacts\u00a3/g, '\u00a3minor_artifacts\u00a3');
    out = out.replace(/Major \u9996\u90fd \u5efa\u7b51/g, '\u4e3b\u90fd\u5efa\u7b51');
    out = out.replace(/\u56fd\u5bb6 does \u4e0d use \u751f\u7269\u8230\u8239/g, '\u56fd\u5bb6\u4e0d\u4f7f\u7528\u751f\u7269\u8230\u8239');
    out = out.replace(/\u5efa\u9020 Cost/g, '\u5efa\u9020\u82b1\u8d39');
    out = out.replace(/\u5efa\u9020 \u82b1\u8d39\uff1a/g, '\u5efa\u9020\u82b1\u8d39\uff1a');
    out = out.replace(/\u5efa\u9020 \u901f\u5ea6/g, '\u5efa\u9020\u901f\u5ea6');
    out = out.replace(/The\s+\u5e1d\u56fd\u89c4\u6a21\s+\u6548\u679c\s+\u662f\s+\u6539\u9020\u7684\s+by/g, '\u5e1d\u56fd\u89c4\u6a21\u6548\u5e94\u4fee\u6b63\u4e3a');
    out = out.replace(/\u4e0d\s+AI\u6027\u683c\s+\u662f\s+\u6392\u5916\u5b64\u7acb\u4e3b\u4e49/g, 'AI\u6027\u683c\u4e0d\u662f\u6392\u5916\u5b64\u7acb\u4e3b\u4e49');
    out = out.replace(/ \u5355 \u9635\u5217/g, '\u5355\u9635\u5217');
    out = out.replace(/ \u53cc \u9635\u5217/g, '\u53cc\u9635\u5217');
    out = out.replace(/a bulwark \([^)]*\u9644\u5c5e\u56fd\)/gi, '\u5821\u5792\u5b50\u56fd');
    out = out.replace(/a prospectorium \([^)]*\u9644\u5c5e\u56fd\)/gi, '\u52d8\u63a2\u5b50\u56fd');
    out = out.replace(/a scholarium \([^)]*\u9644\u5c5e\u56fd\)/gi, '\u5b66\u8005\u5b50\u56fd');
    out = out.replace(/a bulwark \(specialised \u9644\u5c5e\u56fd\)/gi, '\u5821\u5792\u5b50\u56fd');
    out = out.replace(/a prospectorium \(specialised \u9644\u5c5e\u56fd\)/gi, '\u52d8\u63a2\u5b50\u56fd');
    out = out.replace(/a scholarium \(specialised \u9644\u5c5e\u56fd\)/gi, '\u5b66\u8005\u5b50\u56fd');

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
