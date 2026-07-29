# Overview

┌──────────────────────────────────────────────────────────────────────────────┐
│ 🎓 Grade Tracker                                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Dashboard | Students | Courses | Grades | Statistics | Settings              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              Inhalt des Tabs                                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│ Students                                                    [+ Add Student] │
├──────────────────────────────┬──────────────────────────────────────────────┤
│                              │                                              │
│ Student List                 │ Student Details                              │
│                              │                                              │
│ ┌──────────────────────────┐ │ Name:                                        │
│ │ ID   Name                │ │                                              │
│ │------------------------- │ │ Email:                                       │
│ │ S001 Max Mustermann      │ │                                              │
│ │ S002 Anna Schmidt        │ │ Courses:                                     │
│ │ S003 Peter Wagner        │ │                                              │
│ └──────────────────────────┘ │ Average Grade:                               │
│                              │                                              │
│                              │                                              │
│                              │ [ Edit ]   [ Delete ]                        │
└──────────────────────────────┴──────────────────────────────────────────────┘

# Grade Tracker – UI Architecture

1. Ziel der Benutzeroberfläche
Die Benutzeroberfläche des Grade Trackers soll eine intuitive Verwaltung von akademischen Daten ermöglichen.
Die Anwendung folgt dabei einem klassischen Master-Detail-Pattern:
Auf der linken Seite werden Objekte ausgewählt und verwaltet.
Auf der rechten Seite werden Details angezeigt und Aktionen durchgeführt.
Dieses Muster wird für alle zentralen Entitäten verwendet:
Students
Courses
Grades
Statistics
Dadurch entsteht eine konsistente Benutzererfahrung.

2. Gesamtaufbau der Anwendung
┌─────────────────────────────────────────────────────────────┐
│                        Header                               │
│                                                             │
│   Logo        Grade Tracker             Version             │
│               Academic Management Dashboard                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Dashboard | Students | Courses | Grades | Statistics       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Active Tab Content                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

3. Tab-Struktur
Dashboard
Ziel:
Übersicht über die Anwendung.
Mögliche Inhalte:
┌───────────────────────────┐
│ Total Students            │
│ 120                       │
└───────────────────────────┘


┌───────────────────────────┐
│ Total Courses             │
│ 15                        │
└───────────────────────────┘


┌───────────────────────────┐
│ Average Grade             │
│ 84.5 %                    │
└───────────────────────────┘

Students Tab
Ziel
Verwalten aller Studenten.
Funktionalitäten:
 - Studenten anzeigen
 - Studenten auswählen
 - Details anzeigen
 - Studenten hinzufügen
 - Studenten bearbeiten
 - Studenten löschen
Layout
┌────────────────────────────────────────────────────────────┐
│ Students                                  [+ Add Student] │
├───────────────────────────┬────────────────────────────────┤
│                           │                                │
│ Student List              │ Student Details                │
│                           │                                │
│ ┌───────────────────────┐ │ Name                           │
│ │ ID | Name | Email     │ │ ------------------------------ │
│ │-----------------------│ │                                │
│ │ S001 Max Mustermann   │ │ Email                          │
│ │ S002 Anna Schmidt     │ │                                │
│ │ S003 Peter Müller     │ │ Courses                        │
│ │                       │ │                                │
│ └───────────────────────┘ │ Average Grade                  │
│                           │                                │
│                           │                                │
│                           │ [Edit]       [Delete]          │
└───────────────────────────┴────────────────────────────────┘

## Student Interaction Flow
### Auswahl eines Studenten
User klickt Student

        ↓

Student ID wird an UI-Controller übergeben

        ↓

Store lädt Daten

        ↓

StudentRepository
StatisticsRepository

        ↓

Details werden aktualisiert

### Add Student Workflow
+ Add Student

        ↓

Formular öffnen

        ↓

User gibt Daten ein

        ↓

Student Objekt erzeugen

        ↓

SqliteGradeStore

        ↓

StudentRepository

        ↓

SQLite

        ↓

Liste aktualisieren

### Edit Student Workflow
Student auswählen

        ↓

Details anzeigen

        ↓

Edit Button

        ↓

Formular aktivieren

        ↓

Änderungen speichern

        ↓

StudentRepository.update()

        ↓

Liste aktualisieren

### Delete Student Workflow
Student auswählen

        ↓

Delete Button

        ↓

Bestätigung

        ↓

Store.delete_student()

        ↓

Database Update

        ↓

UI Refresh

## Courses Tab
Struktur identisch:
┌───────────────────────────┬───────────────────────────────┐
│ Course List               │ Course Details                 │
│                           │                               │
│ Mathematics               │ Name                          │
│ Physics                   │ Max Grade                     │
│ Programming               │ Passing Grade                 │
│                           │                               │
│                           │ Students                      │
│                           │                               │
└───────────────────────────┴───────────────────────────────┘


## Grades Tab
Ziel:
Noten erfassen und verwalten.
Workflow:
Student auswählen

        ↓

Course auswählen

        ↓

Grade eingeben

        ↓

Grade Objekt erzeugen

        ↓

GradeRepository

        ↓

SQLite

## Statistics Tab
Darstellung der vorhandenen Statistikfunktionen:
StatisticsRepository

        ↓

SQL Aggregations

        ↓

Visualisierung

Mögliche Ansichten:
 - Durchschnitt pro Kurs
 - Beste Studenten
 - Anzahl Studenten pro Kurs
 - Notenverteilung

## 4. UI Architektur Prinzipien
Trennung von Darstellung und Logik
Die UI kennt keine SQL-Struktur.

### Komponentenorientierter Aufbau
Jeder Tab besitzt eine eigene Datei:
ui/

├── header.py

├── dashboard.py

├── students.py

├── courses.py

├── grades.py

└── statistics.py