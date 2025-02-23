# src.core.types
from enum import Enum


class ID3Keys(Enum):
    TITLE = "TIT2"
    TRACK_SUBTITLE = "TIT3"
    ARTIST = "TPE1"
    ARTIST_SORT = (
        "TSOP"  # Should be "performer sort" but shows up as "artistsort in Quod Libet
    )
    PERFORMER = "TPE2"  # Should be "band" but shows up as performer in Quod Libet
    PERFORMER_SORT = "TXXX:QuodLibet::performersort"
    CONDUCTOR = "TPE3"  # classical music
    INTERPRETER_REMIXER = "TPE4"  # Intrepreter or remixer or modifier.
    INVOLVED_PEOPLE = "TIPL"  # Engineers, producers, mixers...
    ALBUM_ARTIST = "TXXX:QuodLibet::albumartist"
    ALBUM_ARTIST_SORT_ORDER = "TSO2"
    TRACK_NUM = "TRCK"
    DISC_NUM = "TPOS"  # Part of set.
    ALBUM = "TALB"
    ALBUM_SORT_ORDER = "TSOA"
    DISC_SUBTITLE = "TSST"  # Set subtitle.
    # RECORDING_TIME = "TDRC"
    RELEASE_TIME = "TDRC"  # Should be TDRL but TDRC is used by every media player.
    GENRE = "TCON"
    DESCRIPTION = "TXXX:QuodLibet::description"
    LANGUAGE = "TLAN"
    COMPOSER = "TCOM"  # classical music
    COMPOSER_SORT_ORDER = "TSOC"  # classical music
    LABEL = "TPUB"
    LABEL_ID = "TXXX:QuodLibet::labelid"
    MUSICIAN_CREDITS = "TMCL"
    WRITTEN_BY = "TEXT"
    # ISRC = "ISRC"
    BPM = "TBPM"
    MEDIA = "TMED"
    COMPILATION = "TCMP"  # '0' or '1'
    COMMENT = "COMM"
    STATS = "POPM"
    TEST = ""


class Iso6392Codes(Enum):
    English = "eng"
    Chinese = "chi"
    French = "fre"
    Japanese = "jpn"
    Spanish = "spa"
    German = "ger"
    Korean = "kor"
    Russian = "rus"
    Afar = "aar"
    Abkhazian = "abk"
    Achinese = "ace"
    Acoli = "ach"
    Adangme = "ada"
    Adyghe_Adygei = "ady"
    Afro_Asiatic_languages = "afa"
    Afrihili = "afh"
    Afrikaans = "afr"
    Ainu = "ain"
    Akan = "aka"
    Akkadian = "akk"
    Aleut = "ale"
    Algonquian_languages = "alg"
    Southern_Altai = "alt"
    Amharic = "amh"
    English_Old_ca450_1100 = "ang"
    Angika = "anp"
    Apache_languages = "apa"
    Arabic = "ara"
    Official_Aramaic_700_300_BCE_Imperial_Aramaic_700_300_BCE = "arc"
    Aragonese = "arg"
    Armenian = "arm"
    Mapudungun_Mapuche = "arn"
    Arapaho = "arp"
    Artificial_languages = "art"
    Arawak = "arw"
    Assamese = "asm"
    Asturian_Bable_Leonese_Asturleonese = "ast"
    Athapascan_languages = "ath"
    Australian_languages = "aus"
    Avaric = "ava"
    Avestan = "ave"
    Awadhi = "awa"
    Aymara = "aym"
    Azerbaijani = "aze"
    Banda_languages = "bad"
    Bamileke_languages = "bai"
    Bashkir = "bak"
    Baluchi = "bal"
    Bambara = "bam"
    Balinese = "ban"
    Basque = "baq"
    Basa = "bas"
    Baltic_languages = "bat"
    Beja_Bedawiyet = "bej"
    Belarusian = "bel"
    Bemba = "bem"
    Bengali = "ben"
    Berber_languages = "ber"
    Bhojpuri = "bho"
    Bihari_languages = "bih"
    Bikol = "bik"
    Bini_Edo = "bin"
    Bislama = "bis"
    Siksika = "bla"
    Bantu_languages = "bnt"
    Tibetan = "tib"
    Bosnian = "bos"
    Braj = "bra"
    Breton = "bre"
    Batak_languages = "btk"
    Buriat = "bua"
    Buginese = "bug"
    Bulgarian = "bul"
    Burmese = "bur"
    Blin_Bilin = "byn"
    Caddo = "cad"
    Central_American_Indian_languages = "cai"
    Galibi_Carib = "car"
    Catalan_Valencian = "cat"
    Caucasian_languages = "cau"
    Cebuano = "ceb"
    Celtic_languages = "cel"
    Czech = "cze"
    Chamorro = "cha"
    Chibcha = "chb"
    Chechen = "che"
    Chagatai = "chg"
    Chuukese = "chk"
    Mari = "chm"
    Chinook_jargon = "chn"
    Choctaw = "cho"
    Chipewyan_Dene_Suline = "chp"
    Cherokee = "chr"
    Church_Slavic_Old_Slavonic = "chu"
    Chuvash = "chv"
    Cheyenne = "chy"
    Chamic_languages = "cmc"
    Montenegrin = "cnr"
    Coptic = "cop"
    Cornish = "cor"
    Corsican = "cos"
    Creoles_and_pidgins_English_based = "cpe"
    Creoles_and_pidgins_French_based = "cpf"
    Creoles_and_pidgins_Portuguese_based = "cpp"
    Cree = "cre"
    Crimean_Tatar_Crimean_Turkish = "crh"
    Creoles_and_pidgins = "cpr"
    Kashubian = "csb"
    Cushitic_languages = "cus"
    Welsh = "wel"
    Dakota = "dak"
    Danish = "dan"
    Dargwa = "dar"
    Land_Dayak_languages = "day"
    Delaware = "del"
    Slave_Athapascan = "den"
    Dogrib = "dgr"
    Dinka = "din"
    Divehi_Dhivehi_Maldivian = "div"
    Dogri = "doi"
    Dravidian_languages = "dra"
    Lower_Sorbian = "dsb"
    Duala = "dua"
    Dutch_Middle_ca_1050_1350 = "dum"
    Dutch_Flemish = "dut"
    Dyula = "dyu"
    Dzongkha = "dzo"
    Efik = "efi"
    Egyptian_Ancient = "egy"
    Ekajuk = "eka"
    Elamite = "elx"
    English_Middle_1100_1500 = "enm"
    Esperanto = "epo"
    Estonian = "est"
    Ewe = "ewe"
    Ewondo = "ewo"
    Fang = "fan"
    Faroese = "fao"
    Fanti = "fat"
    Fijian = "fij"
    Filipino_Pilipino = "fil"
    Finnish = "fin"
    Finno_Ugrian_languages = "fiu"
    Fon = "fon"
    French_Middle_ca_1400_1600 = "frm"
    French_Old_842_ca_1400 = "fro"
    Northern_Frisian = "frr"
    Eastern_Frisian = "frs"
    Western_Frisian = "fry"
    Fulah = "ful"
    Friulian = "fur"
    Ga = "gaa"
    Gayo = "gay"
    Gbaya = "gba"
    Germanic_languages = "gem"
    Georgian = "geo"
    Geez = "gez"
    Gilbertese = "gil"
    Gaelic_Scottish_Gaelic = "gla"
    Irish = "gle"
    Galician = "glg"
    Manx = "glv"
    German_Middle_High_ca_1050_1500 = "gmh"
    German_Old_High_ca_750_1050 = "goh"
    Gondi = "gon"
    Gorontalo = "gor"
    Gothic = "got"
    Grebo = "grb"
    Greek_Ancient_to_1453 = "grc"
    Swiss_German_Alemannic_Allemanic = "gsw"
    Gujarati = "guj"
    Gwichin = "gwi"
    Haida = "hai"
    Hausa = "hau"
    Hawaiian = "haw"
    Hebrew = "heb"
    Herero = "her"
    Hiligaynon = "hil"
    Himachali_languages_Western_Pahari_languages = "him"
    Hindi = "hin"
    Hittite = "hit"
    Hmong_Mong = "hmn"
    Hiri_Motu = "hmo"
    Croatian = "hrv"
    Upper_Sorbian = "hsb"
    Hungarian = "hun"
    Hupa = "hup"
    Iban = "iba"
    Igbo = "ibo"
    Icelandic = "ice"
    Ido = "ido"
    Sichuan_Yi_Nuosu = "iii"
    Ijo_languages = "ijo"
    Inuktitut = "iku"
    Interlingue_Occidental = "ile"
    Iloko = "ilo"
    Interlingua_International_Auxiliary_Language_Association = "ina"
    Indonesian = "ind"
    Indo_European_languages = "ine"
    Ingush = "inh"
    Inupiaq = "ipk"
    Iranian_languages = "ira"
    Iroquoian_languages = "iro"
    Italian = "ita"
    Javanese = "jav"
    Lojban = "jbo"
    Judeo_Persian = "jpr"
    Judeo_Arabic = "jrb"
    Kara_Kalpak = "kaa"
    Kabyle = "kab"
    Kachin_Jingpho = "kac"
    Kalaallisut_Greenlandic = "kal"
    Kamba = "kam"
    Kannada = "kan"
    Karen_languages = "kar"
    Kashmiri = "kas"
    Kanuri = "kau"
    Kawi = "kaw"
    Kazakh = "kaz"
    Kabardian = "kbd"
    Khasi = "kha"
    Khoisan_other = "khi"
    Central_Khmer = "khm"
    Khotanese_Sakan = "kho"
    Kikuyu_Gikuyu = "kik"
    Kinyarwanda = "kin"
    Kirghiz_Kyrgyz = "kir"
    Kimbundu = "kmb"
    Konkani = "kok"
    Komi = "kom"
    Kongo = "kon"
    Kosraean = "kos"
    Kpelle = "kpe"
    Karachay_Balkar = "krc"
    Karelian = "krl"
    Kru_languages = "kro"
    Kurukh = "kru"
    Kuanyama_Kwanyama = "kua"
    Kumyk = "kum"
    Kurdish = "kur"
    Kutenai = "kut"
    Ladino = "lad"
    Lahnda = "lah"
    Lamba = "lam"
    Lao = "lao"
    Latin = "lat"
    Latvian = "lav"
    Lezghian = "lez"
    Limburgan_Limburger_Limburgish = "lim"
    Lingala = "lin"
    Lithuanian = "lit"
    Mongo = "lol"
    Lozi = "loz"
    Luxembourgish_Letzeburgesch = "ltz"
    Luba_Lulua = "lua"
    Luba_Katanga = "lub"
    Ganda = "lug"
    Luiseno = "lui"
    Lunda = "lun"
    Luo_Kenya_and_Tanzania = "luo"
    Lushai = "lus"
    Macedonian = "mac"
    Madurese = "mad"
    Magahi = "mag"
    Marshallese = "mah"
    Maithili = "mai"
    Moksha = "mdf"
    Mandingo = "man"
    Maori = "mao"
    Marathi = "mar"
    Masai = "mas"
    Malay = "may"
    Mokilese = "mkj"
    Malagasy = "mlg"
    Maltese = "mlt"
    Manchu = "mnc"
    Manipuri = "mni"
    Manobo_languages = "mno"
    Mohawk = "moh"
    Mongolian = "mon"
    Mossi = "mos"
    Multiple_languages = "mul"
    Munda_languages = "mun"
    Creek = "mus"
    Mirandese = "mwl"
    Marwari = "mwr"
    Mayan_languages = "myn"
    Erzya = "myv"
    Nahuatl_languages = "nah"
    North_American_Indian_languages = "nai"
    Neapolitan = "nap"
    Nauru = "nau"
    Navajo_Navaho = "nav"
    South_Ndebele = "nbl"
    North_Ndebele = "nde"
    Ndonga = "ndo"
    Low_German_Low_Saxon_German_Low_Saxon = "nds"
    Nepali = "nep"
    Nepal_Bhasa_Newari = "new"
    Nias = "nia"
    Niger_Kordofanian_languages = "nic"
    Niuean = "niu"
    Norwegian_Nynorsk = "nno"
    Bokmal_Norwegian = "nob"
    Nogai = "nog"
    Norse_Old = "non"
    Norwegian = "nor"
    N_ko = "nqo"
    Pedi_Sepedi_Northern_Sotho = "nso"
    Nubian_languages = "nub"
    Classical_Newari_Old_Newari_Classical_Nepal_Bhasa = "nwc"
    Chichewa_Chewa_Nyanja = "nya"
    Nyamwezi = "nym"
    Nyankole = "nyn"
    Nyoro = "nyo"
    Nzima = "nzi"
    Occitan_post_1500 = "oci"
    Ojibwa = "oji"
    Oriya = "ori"
    Oromo = "orm"
    Osage = "osa"
    Ossetian_Ossetic = "oss"
    Turkish_Ottoman_1500_1928 = "ota"
    Otomian_languages = "oto"
    Papuan_languages = "paa"
    Pangasinan = "pag"
    Pahlavi = "pal"
    Pampanga_Kapampangan = "pam"
    Panjabi_Punjabi = "pan"
    Papiamento = "pap"
    Palauan = "pau"
    Persian_Old_cauc_600_400_B_C = "peo"
    Persian = "per"
    Philippine_languages = "phi"
    Phoenician = "phn"
    Pali = "pli"
    Polish = "pol"
    Pohnpeian = "pon"
    Portuguese = "por"
    Prakrit_languages = "pra"
    Provençal_Old_to_1500_Occitan_Old = "pro"
    Pashto_Pushto = "pus"
    Quechua = "que"
    Rajasthani = "raj"
    Rapanui = "rap"
    Rarotongan_Cook_Islands_Maori = "rar"
    Romance_languages = "roa"
    Romansh = "roh"
    Romany = "rom"
    Romanian = "rum"
    Rundi = "run"
    Sandawe = "sad"
    Sango = "sag"
    Yakut = "sah"
    South_American_Indian_languages = "sai"
    Salishan_languages = "sal"
    Samaritan_Aramaic = "sam"
    Sanskrit = "san"
    Sasak = "sas"
    Santali = "sat"
    Sicilian = "scn"
    Scots = "sco"
    Selkup = "sel"
    Semitic_languages = "sem"
    Irish_Old_to_900 = "sga"
    Sign_Languages = "sgn"
    Shan = "shn"
    Sidamo = "sid"
    Sinhala_Sinhalese = "sin"
    Siouan_languages = "sio"
    Sino_Tibetan_languages = "sit"
    Slavic_languages = "sla"
    Slovak = "slo"
    Slovenian = "slv"
    Southern_Sami = "sma"
    Northern_Sami = "sme"
    Sami_languages = "smi"
    Lule_Sami = "smj"
    Inari_Sami = "smn"
    Samoan = "smo"
    Skolt_Sami = "sms"
    Shona = "sna"
    Sindhi = "snd"
    Soninke = "snk"
    Sogdian = "sog"
    Somali = "som"
    Songhai_languages = "son"
    Sotho_Southern = "sot"
    Spanish_Castilian = "spa"
    Sardinian = "srd"
    Sranan_Tongo = "srn"
    Serbian = "srp"
    Serer = "srr"
    Nilo_Saharan_languages = "ssa"
    Swati = "ssw"
    Sukuma = "suk"
    Sundanese = "sun"
    Susu = "sus"
    Sumerian = "sux"
    Swahili = "swa"
    Swedish = "swe"
    Classical_Syriac = "syc"
    Syriac = "syr"
    Tahitian = "tah"
    Tai_languages = "tai"
    Tamil = "tam"
    Tatar = "tat"
    Telugu = "tel"
    Timne = "tem"
    Tereno = "ter"
    Tetum = "tet"
    Tajik = "tgk"
    Tagalog = "tgl"
    Thai = "tha"
    Tigré = "tig"
    Tigrinya = "tir"
    Tiv = "tiv"
    Tokelau = "tkl"
    Klingon_tlhIngan_Hol = "tlh"
    Tlingit = "tli"
    Tamashek = "tmh"
    Tonga_Nyasa = "tog"
    Tonga_Tonga_Islands = "ton"
    Tok_Pisin = "tpi"
    Tsimshian = "tsi"
    Tswana = "tsn"
    Tsonga = "tso"
    Turkmen = "tuk"
    Tumbuka = "tum"
    Turkish = "tur"
    Altaic_languages = "tut"
    Tuvalu = "tvl"
    Twi = "twi"
    Tuvinian = "tyv"
    Udmurt = "udm"
    Ugaritic = "uga"
    Uighur_Uyghur = "uig"
    Ukrainian = "ukr"
    Umbundu = "umb"
    Undetermined = "und"
    Urdu = "urd"
    Uzbek = "uzb"
    Vai = "vai"
    Venda = "ven"
    Vietnamese = "vie"
    Volapük = "vol"
    Votic = "vot"
    Wakashan_languages = "wak"
    Wolaitta_Wolaytta = "wal"
    Waray = "war"
    Washo = "was"
    Sorbian_languages = "wen"
    Walloon = "wln"
    Wolof = "wol"
    Kalmyk_Oirat = "xal"
    Xhosa = "xho"
    Yao = "yao"
    Yapese = "yap"
    Yiddish = "yid"
    Yoruba = "yor"
    Yupik_languages = "ypk"
    Zapotec = "zap"
    Blissymbols_Blissymbolics_Bliss = "zbl"
    Zenaga = "zen"
    Standard_Moroccan_Tamazight = "zgh"
    Zhuang_Chuang = "zha"
    Zuni = "zun"
    No_linguistic_content_Not_applicable = "zxx"
    Zaza_Dimili_Dimli_Kirdki_Kirmanjki_Zazaki = "zza"
