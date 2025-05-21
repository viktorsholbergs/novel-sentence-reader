
# Novel Sentence Reader

## Projekta apraksts

**Novel Sentence Reader** ir personalizēta tīmekļa lietotne, kas izstrādāta ar mērķi padarīt "light novels" lasīšanu ērtāku un efektīvāku. Šī sistēma automatizē procesu, kurā lietotājs meklē, lejupielādē un lasa "light novels" saturu. Tradicionāli "light novels" tiek lasītas lielos, nepārtrauktos teksta blokos, kas daudziem lietotājiem var būt grūti pārskatāmi, īpaši, ja teksts nav labi strukturēts. Šis projekts piedāvā risinājumu – sadalīt saturu pa atsevišķiem teikumiem un attēlot tos lietotājam vienu pēc otra, ļaujot koncentrēties uz vienu domu vienlaikus. Tādējādi tiek samazināts kognitīvais slogs un uzlabota teksta uztvere.

Projekts sastāv no divām galvenajām daļām: tīmekļa skrāpēšanas skripta un pašas lietotnes. Tīmekļa skripts, izmantojot Selenium bibliotēku, apmeklē vietni [lightnovelworld.co](https://www.lightnovelworld.co) – populāru "light novels" platformu – un automātiski lejupielādē visus "light novel" pieejamos nodaļu tekstus, sākot no lietotāja norādītās pirmās nodaļas saites. Katras nodaļas saturs tiek apstrādāts, notīrot liekos HTML elementus, un tiek saglabāts lokāli kā vienkāršs teksts atsevišķos failos `novels` mapē.

Pēc tam šie teksti tiek sadalīti teikumos, izmantojot NLTK bibliotēkas `sent_tokenize` funkcionalitāti. Apstrādātie dati tiek iekļauti dubultā saistītajā sarakstā – pielāgotā datu struktūrā, kas atvieglo navigāciju starp teikumiem uz priekšu un atpakaļ. Šī struktūra ir būtiska, jo tā ļauj saglabāt informāciju par pašreizējo teikumu, iepriekšējo un nākamo, kas ir svarīgi lasīšanas plūsmas nodrošināšanai.

Otra projekta daļa ir tīmekļa lietotne, kas balstīta uz Flask ietvaru. Tā nodrošina divas galvenās saskarnes – `select.html`, kurā lietotājs var pievienot jaunu "light novel" saiti vai izvēlēties jau lejupielādētu darbu, un `reader.html`, kurā tiek attēlots viens teikums vienlaikus. Lietotājs var izmantot pogas vai tastatūras bulttaustiņus, lai pārvietotos starp teikumiem. Pēc pēdējā teikuma vienā nodaļā lietotne automātiski pāriet uz nākamo nodaļu. Saskarne ļauj arī mainīt fontu, fona un teksta krāsas, lai pielāgotu pieredzi savām vajadzībām.

Šis rīks tika veidots ar domu par vienkāršību un funkcionalitāti, ņemot vērā, ka tas tiks izmantots tikai lokāli un vienam lietotājam. Tādēļ nav ieviestas lietotāju autentifikācijas vai datubāzu sistēmas, kas būtu nepieciešamas, ja programmatūra tiktu izmantota publiski. Taču šis dizains padara projektu piemērotu kā pamatu turpmākai attīstībai.

Kopsavilkumā, **Novel Sentence Reader** piedāvā vieglāku pieeju "light novels" lasīšanai, padarot to  viegli lasāmu. Tas ne tikai automatizē datu iegūšanu un struktūrizēšanu, bet arī uzlabo lietotāja pieredzi, izmantojot vienkāršu, bet efektīvu saskarni. Šis projekts ir lielisks piemērs tam, kā datu struktūru un algoritmu zināšanas var pielietot praktiskā, ikdienā noderīgā risinājumā.

## Izmantotās Python bibliotēkas un to pielietojums

Projekta izstrādes laikā tika izmantotas šādas Python bibliotēkas:

- **Flask**: tīmekļa lietotnes izveidei un maršrutēšanai.
- **Selenium**: tīmekļa lapu automatizētai apstrādei un datu iegūšanai no lightnovelworld.co.
- **NLTK (Natural Language Toolkit)**: teksta sadalīšanai teikumos.
- **json**: datu saglabāšanai un apmaiņai starp serveri un klientu.
- **os**: failu sistēmas darbību veikšanai.
- **re**: regulāro izteiksmju izmantošanai teksta apstrādē.
- **threading**: fona procesu izpildei, lai neapturētu galveno lietotnes darbību.
- **webdriver_manager**: automātiskai ChromeDriver pārvaldībai.

Šīs bibliotēkas tika izvēlētas, lai nodrošinātu efektīvu tīmekļa satura iegūšanu, teksta apstrādi un lietotnes darbību.

## Izmantotās datu struktūras

Projektā tika izveidota un izmantota **dubultā saistītā saraksta** (double linked list) datu struktūra, lai pārvaldītu teikumu secību katrā nodaļā. Šī struktūra ļauj lietotājam:

- Pāriet uz nākamo vai iepriekšējo teikumu.
- Sekot līdzi lasīšanas progresam.
- Automātiski pāriet uz nākamo nodaļu pēc pašreizējās pabeigšanas.

Šāda pieeja nodrošina elastīgu un lietotājam draudzīgu lasīšanas pieredzi.

## Lietotnes izmantošana

### 1. Novela pievienošana

- Apmeklējiet [lightnovelworld.co](https://www.lightnovelworld.co) un atrodiet vēlamo vieglo romānu.
- Nokopējiet saiti uz pirmo nodaļu.
- Atveriet `select.html` failu savā pārlūkprogrammā.
- Ievietojiet saiti ievades laukā un nospiediet "Add Novel".

### 2. Lasīšanas uzsākšana

- Pēc novela pievienošanas, tā parādīsies sarakstā.
- Noklikšķiniet uz vēlamā romāna, lai sāktu lasīšanu.

### 3. Lasīšanas režīms (`reader.html`)

- Tiek parādīts viens teikums vienlaikus.
- Lietotājs var izmantot pogas vai bultu taustiņus, lai pārvietotos starp teikumiem.
- Pēc nodaļas pēdējā teikuma automātiski tiek ielādēta nākamā nodaļa.
- Ir iespēja pielāgot fonta izmēru, krāsu un fonu.

## 📂 Projekta struktūra

```
novel-sentence-reader/
├── app.py
├── lightnovel_scraper.py
├── novels/
│   └── [novela_nosaukums]/
│       ├── chapter_1.txt
│       ├── chapter_2.txt
│       └── ...
├── templates/
│   ├── select.html
│   └── reader.html
├── static/
│   ├── style.css
│   └── script.js
└── README.md
```

- `app.py`: Galvenais Flask servera fails.
- `lightnovel_scraper.py`: Skripts, kas iegūst un saglabā romāna nodaļas.
- `novels/`: Katalogs, kurā tiek saglabātas lejupielādētās nodaļas.
- `templates/`: HTML veidnes lietotnes saskarnei.
- `static/`: CSS un JavaScript faili lietotnes izskatam un funkcionalitātei.

## Sistēmas prasības un uzstādīšana

### Prasības

- Python 3.8 vai jaunāka versija
- Google Chrome pārlūkprogramma
- ChromeDriver (automātiski pārvaldīts ar `webdriver_manager`)

### Uzstādīšana

1. Klonējiet repozitoriju:

   ```bash
   git clone https://github.com/viktorsholbergs/novel-sentence-reader.git
   cd novel-sentence-reader
   ```

2. Instalējiet nepieciešamās bibliotēkas:

   ```bash
   pip install flask selenium nltk lightnovel-scraper
   ```

3. Palaidiet lietotni:

   ```bash
   python app.py
   ```

4. Atveriet pārlūkprogrammā `http://localhost:5000/select.html`



## Piezīmes

- Lietotne ir paredzēta tikai lokālai lietošanai un nav piemērota publiskai izvietošanai bez papildu drošības pasākumiem.
- Projekts ir izstrādāts kā individuāls noslēguma darbs datu struktūru un algoritmu kursā.

Ja jums nepieciešama papildu palīdzība vai ir jautājumi, lūdzu, sazinieties ar mani.
