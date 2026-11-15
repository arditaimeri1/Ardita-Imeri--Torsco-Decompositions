# Torso Decompositions (SpOC 3, Challenge 1)

Projekt për lëndën DAA, bazuar në sfidën Torso Decompositions të ESA-s (SpOC 3, GECCO 2024).

## Problemi
Jepet një graf i padrejtuar me n nyje. Zgjidhja është një permutacion i nyjeve dhe një numër t.
Nyjet eliminohen sipas permutacionit, dhe n − t nyjet e fundit formojnë torson.
Dy objektivat janë torso sa më e madhe dhe gjerësia (maksimumi i skajeve dalëse brenda torsos)
sa më e vogël. Fronti Pareto vlerësohet me hypervolume.

## Çka përmban kjo repo tani
- `torso.py`: leximi i grafit dhe funksionet e vlerësimit.

## Statusi
Projekti është në zhvillim. Rezultatet e para për grafin e vogël (llogaritur nga kodi im,
pa u verifikuar ende me vlerësuesin zyrtar) do të shtohen këtu kur të jenë të sigurta.

## Burimi
Repo zyrtare e sfidës: https://github.com/esa/SpOC3