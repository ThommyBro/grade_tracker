Projektidee und Ziel
Architekturüberblick
Domänenmodell
Datenbankdesign
Repository Pattern
Store-Abstraktion
InMemory vs. SQLite Implementierung
Datenfluss anhand typischer Operationen
Testing-Strategie
Wichtige Designentscheidungen und Erkenntnisse
Aktueller Stand und nächste Schritte


Grade Tracker – Architektur- und Entwicklungsdokumentation
1. Projektidee
Der Grade Tracker ist eine kleine akademische Verwaltungsanwendung zur Verwaltung von:
 - Studenten
 - Kursen
 - Noten
Das Ziel des Projektes war nicht nur eine funktionierende Anwendung zu bauen, sondern typische Konzepte aus Software Engineering praktisch anzuwenden:
 - Objektorientierung
 - Clean Code
 - Separation of Concerns
 - Repository Pattern
 - Dependency Inversion
 - Unit Testing
 - Datenbankpersistenz
 - Abstraktion von Datenquellen
Die Anwendung soll später über eine Gradio-Oberfläche bedienbar sein.


2. Gesamtarchitektur
Die Anwendung ist in mehrere Schichten aufgeteilt.
Ein vereinfachtes Architekturdiagramm:
```
                    User
                     |
                     v
              +--------------+
              |    Gradio    |
              +--------------+
                     |
                     v
              +--------------+
              | GradeStore   |
              |   (ABC)      |
              +--------------+
                     |
        +------------+-------------+
        |                          |
        v                          v
+----------------+        +----------------+
| InMemoryStore  |        | SqliteStore    |
+----------------+        +----------------+
        |                          |
        v                          v
+----------------+        +----------------+
|  GradeBook     |        | Repositories   |
+----------------+        +----------------+
                                   |
                                   v
                              +---------+
                              | SQLite  |
                              +---------+
```

3. Domänenmodell
Das Domänenmodell beschreibt die fachlichen Objekte.
Die wichtigsten Klassen:
```
             +-------------+
             |   Student   |
             +-------------+
             | student_id  |
             | first_name  |
             | last_name   |
             | email       |
             +-------------+


             +-------------+
             |   Course    |
             +-------------+
             | course_id   |
             | name        |
             | max_grade   |
             | passing     |
             +-------------+


             +-------------+
             |    Grade    |
             +-------------+
             | student     |
             | course      |
             | score       |
             | date        |
             | notes       |
             +-------------+
````

4. Dataclasses als Datenmodelle
Für die Domänenobjekte wurden Python dataclasses verwendet.
beispiel:
````
@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    email: str
````
Vorteile:
 - weniger Boilerplate
 - automatische __init__
 - bessere Lesbarkeit
 - ideal für Datenobjekte

 5. Persistenzschicht mit SQLite
Für dauerhafte Speicherung wird SQLite verwendet.
Die Datenbank besteht aus drei Haupttabellen:
```
+-------------+
| students    |
+-------------+
| student_id  |
| first_name  |
| last_name   |
| email       |
+-------------+


+-------------+
| courses     |
+-------------+
| course_id   |
| name        |
| max_grade   |
| passing     |
+-------------+


+-------------+
| grades      |
+-------------+
| id          |
| student_id  |
| course_id   |
| score       |
| date        |
| notes       |
+-------------+
```

Die Beziehungen:
```
students
    |
    | 1
    |
    | n
grades
    |
    | n
    |
    | 1
courses
```
Eine Grade-Tabelle enthält also die Fremdschlüssel:
```
grades.student_id
grades.course_id
```
6. Warum gibt es GradeRecord?
Eine wichtige Designentscheidung war die Trennung zwischen:
Domain Objekt:  Grade
und
Datenbank Objekt: GradeRecord

Die Datenbank besitzt technische Informationen:
```
SQLite:

grades
 |
 + id INTEGER PRIMARY KEY
```

Die Fachlogik braucht diese ID aber nicht.
Deshalb:
```
Domain Layer

  Grade
    |
    |
    v

Persistence Layer

GradeRecord
    |
    |
    v

  SQLite
````

Die Umwandlung:
`GradeRecord.from_grade(grade)`
macht aus: `Grade(
    student,
    course,
    90,
    "2026-07-20"
)`
ein Datenbankobjekt: `GradeRecord(
    student_id="12345",
    course_id="101",
    score=90,
    date="2026-07-20"
)`


7. Repository Pattern
Die SQL-Logik wurde aus dem Store ausgelagert.
Beispiel:
````
SqliteGradeStore

       |
       v

GradeRepository

       |
       v

SQLite
```
Das Repository kümmert sich ausschließlich um Datenbankoperationen.


8. GradeStore Abstraktion
Damit verschiedene Speicherarten möglich sind, wurde ein Interface eingeführt:
`class GradeStore(ABC):`
mit Methoden wie:
````
add_student()

get_student()

add_grade()

update_grade()

delete_grade()
```

Implementierungen:
```
              GradeStore

                  |
       +----------+----------+
       |                     |
       v                     v

 InMemoryStore        SqliteStore
```
Beide müssen dieselben Methoden anbieten.
Dadurch können Tests gegen beide Implementierungen laufen.

9. CRUD für Grades
Die komplette CRUD-Logik ist umgesetzt.
CREATE
```
Grade
 |
 v
GradeRecord
 |
 v
INSERT
 |
 v
SQLite
```

READ
```
SQLite
 |
 v
Repository
 |
 v
Grade
```

UPDATE
Beispiel:
```
grade.score = 95
store.update_grade(grade)
```
Ablauf:
```
Grade

 |
 |
 v

GradeRecord.from_grade()

 |
 |
 v

UPDATE grades
```

DELETE
Beispiel: `store.delete_grade(grade)``
Ablauf:
```
Grade

 |
 |
 v

GradeRecord

 |
 |
 v

DELETE FROM grades
```

Identifikation:
student_id
course_id
date


10. Testing Strategie
Das Projekt verwendet pytest.
Die Tests prüfen nicht nur einzelne Klassen, sondern auch das Verhalten der Stores.
Beispiel:
```
             Test

              |
              v

        GradeStore Interface

              |
       +------+------+
       |             |
       v             v

 InMemory       SQLite
```
Dadurch wird sichergestellt:
Beide Implementierungen verhalten sich gleich.

Beispiel: 
```
grade = store.get_student_grades("12345")[0]

grade.score = 95

store.update_grade(grade)

updated = store.get_student_grades("12345")

assert updated[0].score == 95
```


11. Wichtige Architekturentscheidungen
Entscheidung 1: Keine Datenbank-ID im Grade Objekt. Die Domain sollte unabhängig von der Datenbank bleiben.
Entscheidung 2: Repository trennt SQL und Anwendung
--> Vorteil:
leichter testbar
leichter austauschbar
klarere Verantwortlichkeiten

Entscheidung 3: Gleiche Tests für verschiedene Speicher. Durch GradeStore können beide Implementierungen getestet werden.
Das ist ein Beispiel für 'Dependency Inversion Principle'