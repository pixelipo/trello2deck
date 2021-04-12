# trello2deck
Fetch data from Trello and import into Nextcloud Deck via respective APIs

## Installation

- Clone repository
- Ensure you have Python 3.7+ installed as well as all dependencies
- Generate a private Trello key/token pair at https://trello.com/app-key
- Copy `.env.sample` to `.env` and add your Trello key/token pair
- Add your Nextcloud instance URL to `.env` file


## Running

- Start by running `main.py` application
- Select which service you want to run

### Services

 1. __Import from Trello__ - imports Boards, Lists and Cards from Trello into an internal SQLite database
 2. __Import from JSON__ - imports from a JSON export file **[TODO]**
 3. Authenticate with Deck - walks you through authentication with your Nextcloud instance. Returns `DECK_PASSWORD` value to save to `.env` file.
 4. Export to Deck - Export Decks, Stacks and Cards from SQLite to Deck **[BROKEN]**


 ### What works
- import Trello Boards (active, archived, starred, date modified)
- import Trello Lists (active and archived, remebers position)
- import Trello Cards (opened and closed, due and modified dates, title, description and position)
- keep and eye on Trello API rate limits
- Nextcloud authentication via Nextcloud interface; generates app password to be used for API calls
- establish connection with Deck's REST API


 ### TODO
 - refactor export to Deck
 - import Trello Card labels
 - import Trello Card attachments
 - import from JSON file
 - establish two-way synchronization between Deck and Trello
 - refactor code (make object-oriented)
 - use proper Trello authentication
