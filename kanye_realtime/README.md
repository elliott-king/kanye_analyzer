# TODOS:
- Consider moving to python on the backend.

### High Priority:
- Rerun python model every so often (taking into account user classification).
- Change nlp classifier based on given input.
- Better integrate python & node using rabbitMQ: https://medium.com/@HolmesLaurence/integrating-node-and-python-6b8454bfc272
- Add more unit tests (start applying TDD).

### Med Priority:
- Modify colors of pie chart to be more distinctive.
- Re-label pie chart.
- Python server should restart upon code change.

### Low priority:
- In react select for user classification, user should have a null option.
- Get rid of column name in 'args' (server arguments).
- Name server file 'app.js'
- Reinforce (on client and server) that data is JSON format
- style.css is being duplicated (incl. @ index.js, also copies w/ webpack.config)
- Move to PostgreSQL
- consider splitting the website and scraper
    a) Redis to communicate
    b) Postgres event notification
    c) Server-sent events: https://www.html5rocks.com/en/tutorials/eventsource/basics/#toc-js-api

