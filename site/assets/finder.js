// Shared postcode-distance finder for teslaservice.co.uk.
// Requires ALL_GARAGES (from assets/garages-data.js) to be loaded first, and these
// elements to exist on the page: #search, #searchBtn, #filterCategory (optional),
// #listings, #empty, #finderNote (optional).
//
// Every garage's coordinates are pre-computed in garages-data.js (lat/lon), so a search
// needs just ONE request to postcodes.io (free, no API key) to locate the visitor's
// postcode or outcode — then distances are calculated instantly in the browser.

const CATEGORY_LABEL = {
  dealer: "Official Tesla Service Centre",
  authorised: "Tesla-Approved Bodyshop",
  hevra: "HEVRA-Accredited EV Specialist",
  other: "Independent / Other Tesla Servicing",
  parts: "Parts, Accessories & Cosmetic",
};

const TS_PLACES = [["Bedfordshire",52.03,-0.45,"/locations/county/bedfordshire"],["Berkshire",51.45,-1.0,"/locations/county/berkshire"],["Buckinghamshire",51.8,-0.8,"/locations/county/buckinghamshire"],["Cambridgeshire",52.38,0.05,"/locations/county/cambridgeshire"],["Cheshire",53.2,-2.55,"/locations/county/cheshire"],["Cornwall",50.4,-4.9,"/locations/county/cornwall"],["Cumbria",54.55,-2.95,"/locations/county/cumbria"],["Derbyshire",53.05,-1.55,"/locations/county/derbyshire"],["Devon",50.72,-3.8,"/locations/county/devon"],["Dorset",50.78,-2.25,"/locations/county/dorset"],["County Durham",54.68,-1.75,"/locations/county/county-durham"],["Durham",54.68,-1.75,"/locations/county/county-durham"],["East Riding of Yorkshire",53.85,-0.55,"/locations/county/east-riding-of-yorkshire"],["East Sussex",50.93,0.2,"/locations/county/east-sussex"],["Essex",51.78,0.55,"/locations/county/essex"],["Gloucestershire",51.8,-2.2,"/locations/county/gloucestershire"],["Greater Manchester",53.5,-2.3,"/locations/county/greater-manchester"],["Hampshire",51.05,-1.25,"/locations/county/hampshire"],["Herefordshire",52.08,-2.75,"/locations/county/herefordshire"],["Hertfordshire",51.8,-0.25,"/locations/county/hertfordshire"],["Isle of Wight",50.68,-1.3,"/locations/county/isle-of-wight"],["Kent",51.2,0.75,"/locations/county/kent"],["Lancashire",53.85,-2.6,"/locations/county/lancashire"],["Leicestershire",52.65,-1.15,"/locations/county/leicestershire"],["Lincolnshire",53.1,-0.25,"/locations/county/lincolnshire"],["Merseyside",53.45,-2.95,"/locations/county/merseyside"],["Norfolk",52.65,1.0,"/locations/county/norfolk"],["North Yorkshire",54.1,-1.45,"/locations/county/north-yorkshire"],["Northamptonshire",52.3,-0.85,"/locations/county/northamptonshire"],["Northumberland",55.25,-2.0,"/locations/county/northumberland"],["Nottinghamshire",53.1,-1.0,"/locations/county/nottinghamshire"],["Oxfordshire",51.75,-1.3,"/locations/county/oxfordshire"],["Rutland",52.66,-0.63,"/locations/county/rutland"],["Shropshire",52.65,-2.7,"/locations/county/shropshire"],["Somerset",51.15,-2.9,"/locations/county/somerset"],["South Yorkshire",53.5,-1.3,"/locations/county/south-yorkshire"],["Staffordshire",52.85,-2.05,"/locations/county/staffordshire"],["Suffolk",52.2,1.0,"/locations/county/suffolk"],["Surrey",51.25,-0.4,"/locations/county/surrey"],["Tyne and Wear",54.95,-1.55,"/locations/county/tyne-and-wear"],["Warwickshire",52.3,-1.55,"/locations/county/warwickshire"],["West Sussex",50.95,-0.45,"/locations/county/west-sussex"],["West Yorkshire",53.75,-1.65,"/locations/county/west-yorkshire"],["Wiltshire",51.3,-1.95,"/locations/county/wiltshire"],["Worcestershire",52.2,-2.2,"/locations/county/worcestershire"],["Anglesey",53.28,-4.35,"/locations/county/anglesey"],["Gwynedd",52.9,-3.9,"/locations/county/gwynedd"],["Conwy",53.15,-3.75,"/locations/county/conwy"],["Denbighshire",53.1,-3.35,"/locations/county/denbighshire"],["Flintshire",53.2,-3.15,"/locations/county/flintshire"],["Powys",52.35,-3.4,"/locations/county/powys"],["Ceredigion",52.25,-4.0,"/locations/county/ceredigion"],["Pembrokeshire",51.85,-4.9,"/locations/county/pembrokeshire"],["Carmarthenshire",51.9,-4.15,"/locations/county/carmarthenshire"],["Neath Port Talbot",51.65,-3.75,"/locations/county/neath-port-talbot"],["Bridgend",51.55,-3.6,"/locations/county/bridgend"],["Vale of Glamorgan",51.43,-3.4,"/locations/county/vale-of-glamorgan"],["Rhondda Cynon Taf",51.65,-3.4,"/locations/county/rhondda-cynon-taf"],["Merthyr Tydfil",51.75,-3.37,"/locations/county/merthyr-tydfil"],["Blaenau Gwent",51.77,-3.19,"/locations/county/blaenau-gwent"],["Torfaen",51.7,-3.05,"/locations/county/torfaen"],["Monmouthshire",51.78,-2.85,"/locations/county/monmouthshire"],["Aberdeen",57.15,-2.1,"/locations/county/aberdeen-city"],["Aberdeenshire",57.25,-2.6,"/locations/county/aberdeenshire"],["Angus",56.7,-2.9,"/locations/county/angus"],["Argyll and Bute",56.3,-5.3,"/locations/county/argyll-and-bute"],["Clackmannanshire",56.15,-3.75,"/locations/county/clackmannanshire"],["Dumfries and Galloway",55.05,-3.9,"/locations/county/dumfries-and-galloway"],["Dundee",56.47,-2.97,"/locations/county/dundee"],["East Ayrshire",55.5,-4.3,"/locations/county/east-ayrshire"],["East Dunbartonshire",55.94,-4.2,"/locations/county/east-dunbartonshire"],["East Lothian",55.95,-2.75,"/locations/county/east-lothian"],["East Renfrewshire",55.77,-4.35,"/locations/county/east-renfrewshire"],["Fife",56.22,-3.1,"/locations/county/fife"],["Highland",57.45,-4.9,"/locations/county/highland"],["Inverclyde",55.92,-4.73,"/locations/county/inverclyde"],["Midlothian",55.83,-3.1,"/locations/county/midlothian"],["Moray",57.5,-3.25,"/locations/county/moray"],["North Ayrshire",55.7,-4.75,"/locations/county/north-ayrshire"],["North Lanarkshire",55.87,-3.95,"/locations/county/north-lanarkshire"],["Orkney",59.0,-3.0,"/locations/county/orkney"],["Perth and Kinross",56.55,-3.6,"/locations/county/perth-and-kinross"],["Renfrewshire",55.84,-4.55,"/locations/county/renfrewshire"],["Scottish Borders",55.55,-2.8,"/locations/county/scottish-borders"],["Shetland",60.3,-1.25,"/locations/county/shetland"],["South Ayrshire",55.35,-4.65,"/locations/county/south-ayrshire"],["South Lanarkshire",55.6,-3.8,"/locations/county/south-lanarkshire"],["Stirling",56.2,-4.3,"/locations/county/stirling"],["West Dunbartonshire",55.95,-4.5,"/locations/county/west-dunbartonshire"],["West Lothian",55.9,-3.55,"/locations/county/west-lothian"],["County Antrim",54.8,-6.2,"/locations/county/county-antrim"],["Antrim",54.8,-6.2,"/locations/county/county-antrim"],["County Armagh",54.3,-6.6,"/locations/county/county-armagh"],["Armagh",54.3,-6.6,"/locations/county/county-armagh"],["County Down",54.35,-5.9,"/locations/county/county-down"],["Down",54.35,-5.9,"/locations/county/county-down"],["County Fermanagh",54.35,-7.6,"/locations/county/county-fermanagh"],["Fermanagh",54.35,-7.6,"/locations/county/county-fermanagh"],["County Londonderry",54.9,-6.9,"/locations/county/county-londonderry"],["Londonderry",54.9,-6.9,"/locations/county/county-londonderry"],["County Tyrone",54.6,-7.2,"/locations/county/county-tyrone"],["Tyrone",54.6,-7.2,"/locations/county/county-tyrone"],["Na h-Eileanan Siar",57.75,-7.0,"/locations/county/western-isles"],["Western Isles",57.75,-7.0,"/locations/county/western-isles"],["Durham",54.7761,-1.5733,"/locations/durham"],["Isle of Anglesey",53.28,-4.35,"/locations/county/anglesey"],["Ynys Mon",53.28,-4.35,"/locations/county/anglesey"],["Birmingham and Black Country",52.48,-1.9,"/locations/county/west-midlands-county"],["Bangor",53.228,-4.1282,"/locations/bangor"],["Barnsley",53.5535,-1.4826,"/locations/barnsley"],["Bath",51.3828,-2.3593,"/locations/bath"],["Belfast",54.5998,-5.9285,"/locations/belfast"],["Bicester",51.8966,-1.1519,"/locations/bicester"],["Birmingham",52.4793,-1.9029,"/locations/birmingham"],["Blackburn",53.7501,-2.4815,"/locations/blackburn"],["Blackpool",53.8209,-3.0515,"/locations/blackpool"],["Bolton",53.5777,-2.431,"/locations/bolton"],["Bradford",53.7908,-1.7546,"/locations/bradford"],["Brighton",50.8224,-0.1377,"/locations/brighton"],["Bristol",51.4531,-2.601,"/locations/bristol"],["Burnley",53.7875,-2.2444,"/locations/burnley"],["Cambridge",52.2049,0.1197,"/locations/cambridge"],["Canterbury",51.2797,1.0789,"/locations/canterbury"],["Cardiff",51.48,-3.1769,"/locations/cardiff"],["Chelmsford",51.737,0.4736,"/locations/chelmsford"],["Chester",53.1902,-2.8916,"/locations/chester"],["Colchester",51.8897,0.8993,"/locations/colchester"],["Coventry",52.4077,-1.5069,"/locations/coventry"],["Darlington",54.5233,-1.5536,"/locations/darlington"],["Derby",52.9247,-1.4781,"/locations/derby"],["Doncaster",53.5227,-1.1324,"/locations/doncaster"],["Dudley",52.51,-2.0832,"/locations/dudley"],["Dunfermline",56.0712,-3.4639,"/locations/dunfermline"],["Durham",54.7779,-1.5826,"/locations/durham"],["Edinburgh",55.9533,-3.1891,"/locations/edinburgh"],["Exeter",50.7226,-3.5326,"/locations/exeter"],["Falkirk",55.9993,-3.7848,"/locations/falkirk"],["Glasgow",55.8636,-4.2369,"/locations/glasgow"],["Gloucester",51.8646,-2.2469,"/locations/gloucester"],["Grimsby",53.5651,-0.0838,"/locations/grimsby"],["Halifax",53.7228,-1.8602,"/locations/halifax"],["Hereford",52.056,-2.7175,"/locations/hereford"],["Hull",53.7446,-0.3326,"/locations/hull"],["Ipswich",52.0571,1.1528,"/locations/ipswich"],["Kilmarnock",55.6101,-4.4945,"/locations/kilmarnock"],["Lancaster",54.0501,-2.8032,"/locations/lancaster"],["Leeds",53.8007,-1.5503,"/locations/leeds"],["Leicester",52.6336,-1.1335,"/locations/leicester"],["Lincoln",53.2348,-0.5384,"/locations/lincoln"],["Liverpool",53.4093,-2.9785,"/locations/liverpool"],["London",51.5074,-0.1277,"/locations/london"],["Luton",51.8795,-0.4174,"/locations/luton"],["Maidstone",51.273,0.5206,"/locations/maidstone"],["Manchester",53.4789,-2.2453,"/locations/manchester"],["Middlesbrough",54.5764,-1.2368,"/locations/middlesbrough"],["Milton Keynes",52.043,-0.7541,"/locations/milton-keynes"],["Newcastle upon Tyne",54.978,-1.6102,"/locations/newcastle"],["Northampton",52.2379,-0.895,"/locations/northampton"],["Norwich",52.6289,1.2933,"/locations/norwich"],["Nottingham",52.9562,-1.1512,"/locations/nottingham"],["Oldham",53.5422,-2.116,"/locations/oldham"],["Oxford",51.752,-1.2576,"/locations/oxford"],["Paisley",55.8451,-4.4284,"/locations/paisley"],["Perth",56.3955,-3.4389,"/locations/perth"],["Peterborough",52.5725,-0.2425,"/locations/peterborough"],["Plymouth",50.37,-4.1421,"/locations/plymouth"],["Portsmouth",50.7968,-1.0912,"/locations/portsmouth"],["Preston",53.7606,-2.6985,"/locations/preston"],["Reading",51.4538,-0.9738,"/locations/reading"],["Rotherham",53.4307,-1.3547,"/locations/rotherham"],["Sheffield",53.3825,-1.4685,"/locations/sheffield"],["Shrewsbury",52.7082,-2.7543,"/locations/shrewsbury"],["Solihull",52.4128,-1.7775,"/locations/solihull"],["Southampton",50.9049,-1.4043,"/locations/southampton"],["St Albans",51.7523,-0.3391,"/locations/st-albans"],["Stockport",53.408,-2.159,"/locations/stockport"],["Stoke-on-Trent",53.0222,-2.1734,"/locations/stoke-on-trent"],["Sunderland",54.9022,-1.3838,"/locations/sunderland"],["Swansea",51.6267,-3.9404,"/locations/swansea"],["Swindon",51.5615,-1.7855,"/locations/swindon"],["Telford",52.6754,-2.4488,"/locations/telford"],["Wakefield",53.6837,-1.4982,"/locations/wakefield"],["Walsall",52.5862,-1.9803,"/locations/walsall"],["Warrington",53.3896,-2.5909,"/locations/warrington"],["Wigan",53.5455,-2.6297,"/locations/wigan"],["Winchester",51.0618,-1.311,"/locations/winchester"],["Wolverhampton",52.5862,-2.1299,"/locations/wolverhampton"],["Worcester",52.1929,-2.2211,"/locations/worcester"],["Wrexham",53.0479,-2.9948,"/locations/wrexham"],["York",53.962,-1.0837,"/locations/york"],["Harrow",51.571,-0.34,"/locations/harrow"],["Twickenham",51.448,-0.325,"/locations/twickenham"],["Uxbridge",51.546,-0.48,"/locations/uxbridge"],["Watford",51.655,-0.396,"/locations/watford"],["Barnet",51.6497,-0.1712,"/locations/barnet"],["Sutton",51.364,-0.194,"/locations/sutton"],["Slough",51.509,-0.593,"/locations/slough"],["Croydon",51.372,-0.099,"/locations/croydon"],["Bromley",51.406,0.014,"/locations/bromley"],["Maidenhead",51.523,-0.72,"/locations/maidenhead"],["Woking",51.318,-0.558,"/locations/woking"],["High Wycombe",51.629,-0.75,"/locations/high-wycombe"],["Chesterfield",53.2363,-1.4292,"/locations/chesterfield"],["Huddersfield",53.644,-1.782,"/locations/huddersfield"],["Romford",51.577,0.183,"/locations/romford"],["Hemel Hempstead",51.753,-0.472,"/locations/hemel-hempstead"],["Guildford",51.239,-0.576,"/locations/guildford"],["Harrogate",53.994,-1.543,"/locations/harrogate"],["Fareham",50.852,-1.176,"/locations/fareham"],["Aylesbury",51.8171,-0.8107,"/locations/aylesbury"],["Basingstoke",51.2678,-1.0883,"/locations/basingstoke"],["Newport",51.59,-3.007,"/locations/newport"],["Crawley",51.1145,-0.1882,"/locations/crawley"],["Dartford",51.456,0.247,"/locations/dartford"],["Bournemouth",50.721,-1.8767,"/locations/bournemouth"],["Poole",50.719,-1.98,"/locations/poole"],["Southend-on-Sea",51.54,0.711,"/locations/southend-on-sea"],["Cheltenham",51.9007,-2.0767,"/locations/cheltenham"],["Worthing",50.814,-0.371,"/locations/worthing"],["Bedford",52.1368,-0.4685,"/locations/bedford"],["Eastbourne",50.766,0.278,"/locations/eastbourne"],["Mansfield",53.145,-1.196,"/locations/mansfield"],["Nuneaton",52.522,-1.468,"/locations/nuneaton"],["Stevenage",51.902,-0.201,"/locations/stevenage"],["Hastings",50.856,0.581,"/locations/hastings"],["Bury",53.5927,-2.2988,"/locations/bury"],["St Helens",53.455,-2.738,"/locations/st-helens"],["Cheshunt",51.7026,-0.0428,"/locations/cheshunt"],["Rochdale",53.617,-2.157,"/locations/rochdale"],["Runcorn",53.342,-2.731,"/locations/runcorn"],["Welwyn Garden City",51.804,-0.206,"/locations/welwyn-garden-city"],["Dewsbury",53.692,-1.628,"/locations/dewsbury"],["Reigate",51.238,-0.206,"/locations/reigate"],["Bracknell",51.4168,-0.7516,"/locations/bracknell"],["Redditch",52.307,-1.942,"/locations/redditch"],["Lichfield",52.683,-1.827,"/locations/lichfield"],["Tamworth",52.633,-1.692,"/locations/tamworth"],["Brentwood",51.6214,0.3057,"/locations/brentwood"],["Kidderminster",52.388,-2.249,"/locations/kidderminster"],["Basildon",51.5707,0.4524,"/locations/basildon"],["Chatham",51.3849,0.5255,"/locations/chatham"],["Burton upon Trent",52.8074,-1.6448,"/locations/burton-upon-trent"],["Cannock",52.69,-2.0332,"/locations/cannock"],["East Kilbride",55.758,-4.166,"/locations/east-kilbride"],["Farnborough",51.29,-0.755,"/locations/farnborough"],["Harlow",51.769,0.096,"/locations/harlow"],["Ilkeston",52.97,-1.309,"/locations/ilkeston"],["Loughborough",52.772,-1.206,"/locations/loughborough"],["Pontefract",53.692,-1.31,"/locations/pontefract"],["Sevenoaks",51.27,0.192,"/locations/sevenoaks"],["Worksop",53.307,-1.123,"/locations/worksop"],["Cumbernauld",55.945,-3.994,"/locations/cumbernauld"],["Ellesmere Port",53.278,-2.903,"/locations/ellesmere-port"],["Livingston",55.884,-3.519,"/locations/livingston"],["Royal Tunbridge Wells",51.133,0.264,"/locations/royal-tunbridge-wells"],["South Shields",54.998,-1.432,"/locations/south-shields"],["Stafford",52.806,-2.117,"/locations/stafford"],["Braintree",51.8782,0.5531,"/locations/braintree"],["Horsham",51.062,-0.328,"/locations/horsham"],["Keighley",53.867,-1.91,"/locations/keighley"],["Kirkcaldy",56.11,-3.163,"/locations/kirkcaldy"],["Northwich",53.261,-2.512,"/locations/northwich"],["Southport",53.647,-3.007,"/locations/southport"],["Chichester",50.8365,-0.779,"/locations/chichester"],["Stroud",51.745,-2.218,"/locations/stroud"],["Kettering",52.4,-0.728,"/locations/kettering"],["Macclesfield",53.261,-2.126,"/locations/macclesfield"],["Motherwell",55.79,-3.994,"/locations/motherwell"],["Trowbridge",51.32,-2.208,"/locations/trowbridge"],["Wellingborough",52.302,-0.692,"/locations/wellingborough"],["Caerphilly",51.5743,-3.2176,"/locations/caerphilly"],["Crewe",53.095,-2.4418,"/locations/crewe"],["Newbury",51.4,-1.323,"/locations/newbury"],["Royal Leamington Spa",52.292,-1.536,"/locations/royal-leamington-spa"],["Rugby",52.372,-1.263,"/locations/rugby"],["Weston-super-Mare",51.346,-2.976,"/locations/weston-super-mare"],["Banbury",52.0621,-1.3336,"/locations/banbury"],["Chippenham",51.4582,-2.1139,"/locations/chippenham"],["Hartlepool",54.685,-1.213,"/locations/hartlepool"],["Neath",51.664,-3.803,"/locations/neath"],["Greater London",51.507,-0.128,"/locations/greater-london"],["South East",51.3,-0.8,"/locations/south-east"],["South West",50.9,-3.4,"/locations/south-west"],["East of England",52.2,0.6,"/locations/east-of-england"],["East Midlands",52.9,-1.0,"/locations/east-midlands"],["West Midlands",52.48,-1.9,"/locations/west-midlands"],["North West",53.6,-2.6,"/locations/north-west"],["North East",54.95,-1.6,"/locations/north-east"],["Yorkshire",53.9,-1.3,"/locations/yorkshire-and-humber"],["Yorkshire and the Humber",53.9,-1.3,"/locations/yorkshire-and-humber"],["Wales",52.3,-3.6,"/locations/wales"],["Scotland",56.3,-4.0,"/locations/scotland"],["Northern Ireland",54.6,-6.5,"/locations/northern-ireland"],["Scarborough",54.2675,-0.4157,"/locations/scarborough"],["Yeovil",50.952,-2.6055,"/locations/yeovil"],["Bodmin",50.4627,-4.7107,"/locations/bodmin"],["Bridlington",54.0861,-0.1972,"/locations/bridlington"],["Taunton",51.0227,-3.1063,"/locations/taunton"],["Wellington",50.9779,-3.2268,"/locations/wellington"],["St Asaph",53.2556,-3.449,"/locations/st-asaph"],["Salisbury",51.0599,-1.8215,"/locations/salisbury"],["Dorchester",50.7115,-2.4131,"/locations/dorchester"],["Launceston",50.5633,-4.4417,"/locations/launceston"],["Sleaford",52.9873,-0.3769,"/locations/sleaford"],["Driffield",54.0021,-0.4353,"/locations/driffield"],["Malton",54.1333,-0.7886,"/locations/malton"],["Cupar",56.3251,-2.9853,"/locations/cupar"],["Broadstairs",51.3613,1.4321,"/locations/broadstairs"],["Andover",51.2232,-1.5558,"/locations/andover"],["Haverhill",52.0731,0.4292,"/locations/haverhill"],["North Walsham",52.831,1.3813,"/locations/north-walsham"],["Saffron Walden",52.0202,0.2541,"/locations/saffron-walden"],["Folkestone",51.081,1.1415,"/locations/folkestone"],["Petersfield",51.0074,-0.9737,"/locations/petersfield"],["Uckfield",50.9692,0.0893,"/locations/uckfield"],["Sudbury",52.0519,0.7372,"/locations/sudbury"],["Clacton-on-Sea",51.7983,1.154,"/locations/clacton-on-sea"],["Ramsgate",51.3503,1.3203,"/locations/ramsgate"],["Caldicot",51.5904,-2.738,"/locations/caldicot"],["Ely",52.3191,0.2929,"/locations/ely"],["Northallerton",54.3838,-1.4456,"/locations/northallerton"],["Bishop Auckland",54.6473,-1.6662,"/locations/bishop-auckland"],["Ripon",54.1336,-1.5451,"/locations/ripon"],["Market Harborough",52.4851,-0.9054,"/locations/market-harborough"],["Harwich",51.9255,1.2168,"/locations/harwich"],["Sittingbourne",51.3522,0.7379,"/locations/sittingbourne"],["Rye",50.942,0.7479,"/locations/rye"],["Bridgnorth",52.5426,-2.4202,"/locations/bridgnorth"],["Newhaven",50.7887,0.0585,"/locations/newhaven"],["Devizes",51.344,-1.9792,"/locations/devizes"],["Thame",51.7397,-0.9665,"/locations/thame"],["Oxted",51.244,-0.0005,"/locations/oxted"],["Ashby-de-la-Zouch",52.7489,-1.4663,"/locations/ashby-de-la-zouch"],["Brackley",52.0232,-1.1432,"/locations/brackley"],["Wymondham",52.5714,1.1204,"/locations/wymondham"],["Lisburn",54.5151,-6.0707,"/locations/lisburn"],["Clitheroe",53.8769,-2.378,"/locations/clitheroe"],["Clevedon",51.4346,-2.8513,"/locations/clevedon"],["Bishop's Stortford",51.8718,0.1789,"/locations/bishops-stortford"],["Corby",52.5122,-0.6923,"/locations/corby"],["Leek",53.1,-2.0359,"/locations/leek"],["Retford",53.3232,-0.9375,"/locations/retford"],["Waterlooville",50.8969,-1.0171,"/locations/waterlooville"],["Tetbury",51.6413,-2.1569,"/locations/tetbury"],["Portishead",51.4849,-2.7645,"/locations/portishead"],["Carluke",55.7357,-3.8331,"/locations/carluke"],["Skipton",53.952,-2.0125,"/locations/skipton"],["Wokingham",51.3618,-0.8997,"/locations/wokingham"],["Chorley",53.6479,-2.629,"/locations/chorley"],["Witham",51.7966,0.6472,"/locations/witham"],["Swadlincote",52.7349,-1.5329,"/locations/swadlincote"],["Stone",52.9031,-2.1496,"/locations/stone"],["Dursley",51.714,-2.3655,"/locations/dursley"],["Peacehaven",50.8021,0.0098,"/locations/peacehaven"],["Cranleigh",51.1313,-0.4293,"/locations/cranleigh"],["Skelmersdale",53.5416,-2.787,"/locations/skelmersdale"],["Linlithgow",55.981,-3.6286,"/locations/linlithgow"],["Rayleigh",51.5938,0.5903,"/locations/rayleigh"],["Christchurch",50.7374,-1.7423,"/locations/christchurch"],["Blackwood",51.6617,-3.2191,"/locations/blackwood"],["Herne Bay",51.364,1.1018,"/locations/herne-bay"],["Ferndown",50.805,-1.8885,"/locations/ferndown"],["Middlewich",53.189,-2.4392,"/locations/middlewich"],["Letchworth Garden City",51.982,-0.2137,"/locations/letchworth-garden-city"],["Walton-on-Thames",51.3902,-0.4147,"/locations/walton-on-thames"],["Holmfirth",53.5645,-1.8038,"/locations/holmfirth"],["Glenrothes",56.185,-3.1449,"/locations/glenrothes"],["Dorking",51.2397,-0.3236,"/locations/dorking"],["Swanley",51.396,0.1787,"/locations/swanley"],["Leigh",53.5078,-2.5261,"/locations/leigh"],["Castle Donington",52.8494,-1.3385,"/locations/castle-donington"],["Irlam",53.4344,-2.4185,"/locations/irlam"],["Kidlington",51.83,-1.3016,"/locations/kidlington"],["Hitchin",51.9614,-0.2642,"/locations/hitchin"],["Bexhill-on-Sea",50.845,0.4702,"/locations/bexhill-on-sea"],["Farnham",51.2221,-0.7743,"/locations/farnham"],["Keynsham",51.4254,-2.5097,"/locations/keynsham"],["Melksham",51.3593,-2.1305,"/locations/melksham"],["Birkenhead",53.3765,-3.06,"/locations/birkenhead"],["Bathgate",55.8796,-3.6297,"/locations/bathgate"],["Sandhurst",51.3446,-0.8022,"/locations/sandhurst"],["Tonbridge",51.1916,0.2808,"/locations/tonbridge"],["Whitley Bay",55.0541,-1.4621,"/locations/whitley-bay"],["Potters Bar",51.7046,-0.2019,"/locations/potters-bar"],["Darwen",53.6931,-2.4664,"/locations/darwen"],["Leyland",53.7042,-2.688,"/locations/leyland"],["Enfield",51.6469,-0.0491,"/locations/enfield"],["Marlow",51.5722,-0.7615,"/locations/marlow"],["Wickford",51.5891,0.5359,"/locations/wickford"],["Shoreham-by-Sea",50.8334,-0.2912,"/locations/shoreham-by-sea"],["Beeston",52.9183,-1.2101,"/locations/beeston"],["Mirfield",53.68,-1.7115,"/locations/mirfield"],["Bilston",52.5606,-2.0609,"/locations/bilston"],["Chingford",51.6606,-0.0041,"/locations/chingford"],["Eastleigh",50.9435,-1.3651,"/locations/eastleigh"],["Oldbury",52.4932,-2.0116,"/locations/oldbury"],["Thornton-Cleveleys",53.8712,-3.0109,"/locations/thornton-cleveleys"],["Clydebank",55.8956,-4.3991,"/locations/clydebank"],["Heanor",53.0072,-1.3644,"/locations/heanor"],["Newcastle-under-Lyme",53.0279,-2.2439,"/locations/newcastle-under-lyme"],["Bootle",53.45,-3.0007,"/locations/bootle"],["Truro",50.2094,-5.0567,"/locations/truro"],["Inverness",57.4861,-4.2282,"/locations/inverness"],["Dover",51.1279,1.3134,"/locations/dover"],["Newton Abbot",50.5285,-3.611,"/locations/newton-abbot"],["Ashford",51.1465,0.875,"/locations/ashford"],["Orpington",51.373,0.098,"/locations/orpington"],["Wimbledon",51.4214,-0.2064,"/locations/wimbledon"]];

// Town / county / region names typed into the finder (e.g. "Surrey", "Leeds") are matched here
// first, so no postcode is needed. Anything else that isn't a postcode goes to postcodes.io's
// place-name search (towns and villages across the UK).
function tsNorm(s) { return s.toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, " ").replace(/\b(county|co)\b/g, " ").replace(/\s+/g, " ").trim(); }
function tsFindPlace(q) {
  const n = tsNorm(q);
  if (!n) return null;
  let hit = TS_PLACES.find((p) => tsNorm(p[0]) === n);
  if (!hit) { const starts = TS_PLACES.filter((p) => tsNorm(p[0]).startsWith(n)); if (starts.length === 1 || (starts.length && n.length >= 4)) hit = starts[0]; }
  return hit ? { name: hit[0], lat: hit[1], lon: hit[2], url: hit[3] } : null;
}
const TS_POSTCODE_RE = /^[A-Za-z]{1,2}\d[A-Za-z\d]?(\s*\d[A-Za-z]{2})?$/;

function milesBetween(lat1, lon1, lat2, lon2) {
  const R = 3958.8; // miles
  const toRad = (d) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1), dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// Directions row (Google / Apple / Waze / Send to your Tesla), same as teslachargers.co.uk
function tsEsc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
function goRow(d) {
  if (d.lat == null || d.lon == null) return "";
  const p = d.lat + "," + d.lon, addr = d.addr && d.addr !== "Not found" ? d.addr : (d.pc || d.town || "");
  const share = addr ? d.n + ", " + addr : d.n;
  return '<p class="go-sm" role="group" aria-label="Directions to ' + tsEsc(d.n) + '">' +
    '<a class="btn" href="https://www.google.com/maps/dir/?api=1&amp;destination=' + p + '&amp;travelmode=driving" target="_blank" rel="nofollow noopener">Google Maps</a>' +
    '<a class="btn" href="https://maps.apple.com/?daddr=' + p + '&amp;dirflg=d&amp;q=' + encodeURIComponent(d.n) + '" target="_blank" rel="nofollow noopener">Apple Maps</a>' +
    '<a class="btn" href="https://waze.com/ul?ll=' + p + '&amp;navigate=yes" target="_blank" rel="nofollow noopener">Waze</a>' +
    '<button class="btn" type="button" data-share="' + tsEsc(share) + '" data-lat="' + d.lat + '" data-lon="' + d.lon + '">Send to your Tesla</button></p>';
}

function initFinder(opts) {
  const { defaultCategory = "", fixedCategory = null, sampleSize = 8, resultSize = 10 } = opts || {};

  const listEl = document.getElementById("listings");
  const emptyEl = document.getElementById("empty");
  const noteEl = document.getElementById("finderNote");
  const searchInput = document.getElementById("search");
  const searchBtn = document.getElementById("searchBtn");
  const catSelect = document.getElementById("filterCategory");

  if (catSelect && !fixedCategory) catSelect.value = defaultCategory;

  function currentCategory() {
    if (fixedCategory) return fixedCategory;
    return catSelect ? catSelect.value : "";
  }

  function renderRows(rows, distanceKnown) {
    listEl.innerHTML = rows
      .map((d) => {
        const areaBits = [d.town, d.region].filter(Boolean).join(", ");
        const distanceBit = distanceKnown && d.distance != null ? " · " + d.distance.toFixed(1) + " miles away" : "";
        const pcBit = d.pc ? d.pc : areaBits || "Area not publicly listed";
        return `
    <div class="listing">
      <div>
        <h3>${d.n}</h3>
        <div class="meta">${pcBit}${distanceBit}</div>
        <div class="type">${CATEGORY_LABEL[d.c] || d.t}</div>${goRow(d)}
      </div>
      <a class="verify-link" href="${d.url}">Full details →</a>
    </div>`;
      })
      .join("");
    emptyEl.style.display = rows.length ? "none" : "block";
  }

  async function search() {
    const q = searchInput.value.trim();
    const cat = currentCategory();
    const filtered = ALL_GARAGES.filter((d) => !cat || d.c === cat);

    if (!q) {
      if (noteEl) noteEl.textContent = "Enter your postcode, town or county to see the closest results, sorted by real distance.";
      renderRows(filtered.slice(0, sampleSize), false);
      return;
    }

    if (noteEl) noteEl.textContent = "Finding your location…";
    searchBtn.disabled = true;
    try {
      const compact = q.replace(/\s+/g, "");
      let origin = null, label = "", pageLink = "";
      if (!TS_POSTCODE_RE.test(q.trim())) {
        const place = tsFindPlace(q);
        if (place) {
          origin = { lat: place.lat, lon: place.lon }; label = place.name;
          pageLink = place.url;
        } else {
          const pr = await fetch("https://api.postcodes.io/places?q=" + encodeURIComponent(q) + "&limit=1");
          const pj = await pr.json();
          if (pj.status === 200 && pj.result && pj.result.length) {
            origin = { lat: pj.result[0].latitude, lon: pj.result[0].longitude };
            label = pj.result[0].name_1 + (pj.result[0].county_unitary ? ", " + pj.result[0].county_unitary : "");
          }
        }
        if (!origin) {
          if (noteEl) noteEl.textContent = "Couldn't find that place — try a postcode (e.g. M1 1AE or M1), a town or a county.";
          listEl.innerHTML = "";
          emptyEl.style.display = "block";
          return;
        }
      }
      let json = { status: 200, result: { latitude: origin ? origin.lat : null, longitude: origin ? origin.lon : null, postcode: label } };
      if (!origin) {
      let res = await fetch("https://api.postcodes.io/postcodes/" + encodeURIComponent(compact));
      json = await res.json();
      // Fall back to a partial postcode / outcode (e.g. "M1", "BS8") — lots of people only type the first half.
      if ((json.status !== 200 || !json.result) && /^[A-Za-z]{1,2}\d[A-Za-z\d]?$/.test(compact)) {
        res = await fetch("https://api.postcodes.io/outcodes/" + encodeURIComponent(compact));
        json = await res.json();
        if (json.result) json.result.postcode = json.result.outcode;
      }
      if (json.status !== 200 || !json.result) {
        if (noteEl) noteEl.textContent = "Couldn't find that postcode — check it and try again (e.g. M1 1AE or M1), or type a town or county.";
        listEl.innerHTML = "";
        emptyEl.style.display = "block";
        return;
      }
      }
      origin = { lat: json.result.latitude, lon: json.result.longitude };
      const withDistance = filtered
        .map((d) => {
          return d.lat != null ? { ...d, distance: milesBetween(origin.lat, origin.lon, d.lat, d.lon) } : { ...d, distance: null };
        })
        .filter((d) => d.distance != null)
        .sort((a, b) => a.distance - b.distance)
        .slice(0, resultSize);
      if (noteEl) {
        noteEl.textContent = `Closest results to ${json.result.postcode}, sorted by distance.`;
        if (pageLink) {
          const a = document.createElement("a");
          a.href = pageLink; a.textContent = ` See the full ${json.result.postcode} page →`; a.style.color = "var(--accent)";
          noteEl.appendChild(a);
        }
      }
      renderRows(withDistance, true);
    } catch (e) {
      if (noteEl) noteEl.textContent = "Couldn't reach the postcode lookup service right now — try again in a moment.";
    } finally {
      searchBtn.disabled = false;
    }
  }

  // "Use my location": nearest results to the phone's position (nothing is stored or sent anywhere)
  if (navigator.geolocation && searchBtn && searchBtn.parentNode) {
    const geoBtn = document.createElement("button");
    geoBtn.type = "button"; geoBtn.className = "btn"; geoBtn.style.flex = "0 0 auto"; geoBtn.textContent = "Use my location";
    searchBtn.parentNode.insertBefore(geoBtn, searchBtn.nextSibling);
    geoBtn.addEventListener("click", function () {
      if (noteEl) noteEl.textContent = "Finding you…";
      navigator.geolocation.getCurrentPosition(function (pos) {
        const o = { lat: pos.coords.latitude, lon: pos.coords.longitude }, cat = currentCategory();
        const rows = ALL_GARAGES.filter((d) => (!cat || d.c === cat) && d.lat != null)
          .map((d) => ({ ...d, distance: milesBetween(o.lat, o.lon, d.lat, d.lon) }))
          .sort((a, b) => a.distance - b.distance).slice(0, resultSize);
        if (noteEl) noteEl.textContent = "Closest results to your location, sorted by distance.";
        renderRows(rows, true);
      }, function () {
        if (noteEl) noteEl.textContent = "Location is blocked or unavailable. Type a postcode, town or county instead.";
      }, { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 });
    });
  }

  searchBtn.addEventListener("click", search);
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") search();
  });
  if (catSelect) catSelect.addEventListener("change", search);

  const initial = ALL_GARAGES.filter((d) => !defaultCategory || d.c === defaultCategory);
  if (!listEl.querySelector(".listing")) renderRows(initial.slice(0, sampleSize), false);
}
