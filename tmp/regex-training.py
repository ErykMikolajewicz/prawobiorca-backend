import re

text = """
3.  Podstawę prawną Regulaminu stanowią ustawa z dnia 20 lipca 2018 r. Prawo o szkolnictwie 
wyższym  i  nauce  (t.j.  Dz.  U.  z  2023    r.  poz.  742.),  Rozporządzenie  Ministra  Nauki  i Szkolnictwa 
Wyższego z dnia 27 września 2018 r. w sprawie studiów (t.j. Dz. U. z 2024 r. poz. 1571) oraz Statut 
Politechniki Wrocławskiej. 
§ 2. Słownik pojęć 
Użyte w Regulaminie określenia oznaczają: 
1)  absolwent – osoba, która ukończyła studia; 
2)  cykl kształcenia – ciąg następujących po sobie semestrów (cykli dydaktycznych) o dacie 
początku i - wynikającej z przypisanego do niego programu studiów – dacie końca, w których 
realizowane są kolejne etapy studiów z przypisanego programu i planu studiów; 
3)  DZD – Dział Dostępności; 
4)  dziekan – dziekan wydziału, prodziekan wydziału, na którym kształci się student, dyrektor 
filii; 
5)  efekty uczenia się – wiedza, umiejętności i kompetencje społeczne nabyte przez studenta 
w procesie uczenia;  
6)  egzaminator  –  koordynator  przedmiotu  lub  inna  osoba  wskazana  przez  odpowiednio 
dziekana, dyrektora SJO, uprawniona do weryfikacji efektów uczenia się; 
7)  etap  studiów  –  semestr  studiów,  podstawowa  jednostka  składowa  programu  studiów  
realizowana  w  cyklu  dydaktycznym  obejmujący  okres,  w  którym  odbywają  się  zajęcia  oraz 
sesję egzaminacyjną; 
8)  kalendarz  akademicki  –  dokument  określający  szczegółową  organizację 
akademickiego; 
roku 
9)  karta przedmiotu – będący elementem programu studiów opis przedmiotu, określający 
przedmiotowe  efekty  uczenia  się  oraz  treści  programowe  zapewniające  uzyskanie  efektów 
uczenia się w ramach przedmiotu; 
10)  kierunek  studiów  –  wyodrębniona  część  jednego  lub  kilku  obszarów  kształcenia, 
przyporządkowana  co  najmniej  do  jednej  dyscypliny,  realizowana  w  sposób  określony  w 
programie studiów; 
11)  kierunek  standaryzowany  –  kierunek  studiów  przygotowujący  do  wykonywania 
zawodów wymienionych w art. 68 ust 1 Ustawy; 
12)  koordynator przedmiotu – prowadzący zajęcia, a w przypadku grupy zajęć – prowadzący 
zajęcia  wiodące  (końcowe)  w  grupie  zajęć  lub  inna  osoba  wskazana  przez  odpowiednio 
dziekana, dyrektora SJO, dyrektora SWFiS, uprawniona do weryfikacji efektów uczenia się; 
13)  plan studiów – będący elementem programu studiów harmonogram realizacji kolejnych 
etapów studiów na danym kierunku, poziomie, profilu i formie wraz z przypisanymi do tych 
etapów  przedmiotami,  wymiarem  godzinowym 
i  punktowym,  a także  dopuszczalnym 
deficytem punktów ECTS; 
14)  program studiów – efekty uczenia się, przypisane do danego kierunku, poziomu, profilu i 
formy  studiów  oraz  opis  procesu  prowadzącego  do  uzyskania  tych  efektów,  wraz  ze 
wskazaniem liczby punktów ECTS przypisanych do zajęć; 
15)  prowadzący zajęcia – nauczyciel akademicki lub inna osoba, której powierzono realizację 
zajęć; 
16)  przedmiot – określone w programie i planie studiów zajęcia lub grupa zajęć; 
17)  punkty  ECTS  -  punkty  zdefiniowane  w  europejskim  systemie  akumulacji  i transferu 
punktów  (European  Credit  Transfer  System)  jako  miara  średniego  nakładu  pracy  studenta, 
niezbędnego do uzyskania zakładanych efektów uczenia się; 
18)  rozkład  zajęć  –  szczegółowy  harmonogram  realizacji  zajęć  w  danym  semestrze  (cyklu 
dydaktycznym),  określający  w  szczególności  miejsce  i  termin  odbywania  zajęć  wraz  ze 
wskazaniem prowadzącego zajęcia; 
20)  semestr  (cykl  dydaktyczny)  –  semestr  danego  roku  akademickiego,  składający  się 
z okresu, w którym odbywają się zajęcia, sesji egzaminacyjnej oraz przerwy semestralnej; 
21)  student  –  osoba,  która została  przyjęta na  studia  w  Uczelni,  rozpoczęła  studia  i nabyła 
prawa studenta; 
22)  student  ze  szczególnymi  potrzebami  –  student  będący  jednocześnie  osobą  ,  o  której 
mowa w art. 2 pkt 3 ustawy z dnia 19 lipca 2019 r. o zapewnieniu dostępności osobom, ze 
szczególnymi potrzebami (t.j. Dz. U. z 2022 r., poz. 2240); 
23)  system teleinformatyczny –Uniwersytecki System Obsługi Studentów (USOS) służący w 
Uczelni do obsługi toku studiów oraz do komunikacji ze studentami drogą elektroniczną; 
24)  tok  studiów  –  przebieg  studiów  danego  studenta,  na  który  składają  się  wynikające 
z programu studiów etapy studiów oraz wykorzystane urlopy i powtarzane etapy studiów, od 
pierwszego etapu studiów do uzyskania dyplomu ukończenia studiów; 
25)  Ustawa – Ustawa z dnia 20 lipca 2018 r. Prawo o szkolnictwie wyższym i nauce; 
26)  wydział – podstawowa jednostka organizacyjna Uczelni, której podstawowymi zadaniami 
są  kształcenie  i  działalność  naukowa,  prowadząca  studia  na  określonych  kierunkach, 
poziomach, profilu i formie; 
27)  zapisy (rejestracja) na zajęcia - zapisanie na zajęcia w ramach przedmiotu; 
§ 3. Kierunki, poziomy, profile i formy studiów 
1.  Uczelnia  prowadzi  kształcenie  na  studiach  na  określonym  kierunku,  poziomie,  profilu 
i w określonej formie. 
2.  Studia prowadzone są na poziomie studiów pierwszego stopnia, studiów drugiego stopnia oraz 
jako jednolite studia magisterskie. 
3.  Studia mogą być prowadzone na profilu ogólnoakademickim lub praktycznym. 
4.  Studia mogą być prowadzone w formie studiów stacjonarnych lub niestacjonarnych. 
5.  Uczelnia  prowadzi  studia  wspólne  na  warunkach  określonych  w  Ustawie.  W  przypadku 
prowadzenia  studiów  wspólnych  dopuszcza  się,  za  zgodą  Rektora,  odstępstwa  od  postanowień 
niniejszego  Regulaminu,  wynikające  z  postanowień  zawartej  umowy  o  współpracy,  określającej 
zasady realizacji tych studiów. 
"""


PARAGRAPH_CORE = r"§\s+(?P<p_num>\d+)[\.|\)]\s+(?P<p_title>[^\n]+)"
PARAGRAPH_ANCHORED = rf"^{PARAGRAPH_CORE}$"
PARAGRAPH_PLAIN = r"§\s+\d+[\.|\)]\s+[^\n]+$"
PARAGRAPH_BLOCK = rf"{PARAGRAPH_ANCHORED}\n(?P<p_body>.*?)(?={PARAGRAPH_PLAIN}|\Z)"
FLAGS = re.MULTILINE | re.DOTALL

matches = re.finditer(PARAGRAPH_BLOCK, text, FLAGS)

a = []

print(bool(len(a)))
