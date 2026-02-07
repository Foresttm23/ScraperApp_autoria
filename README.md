# Web Scraper

### This app allows scraping data to a `PostgreSQL` database and then dumping it to a `.csv` file at a specified time.

### The scraping website is https://auto.ria.com and is used for educational purposes only.

### The scraping itself is done using an async `Playwright` framework.

### To scrape the paginated data over the number of pages, the app first checks the main page and finds all the links to the car pages, then the pages itself are scraped, and the process repeats until all pages are scraped.

### To speed up scraping, the app uses async db connection, async `playwright` and asyncio semaphore to limit the number of concurrent requests (so the website doesn't block the app for too many requests).

### Since the app is supposed to be automatic, and scrape all the data from the website pages, it uses retries and backoff strategies from the `tenacity` library to avoid getting blocked by the website.

### At the end of scraping the data is saved to the database; to anylyze it later, we can dump the data to a `.csv` file using queries.

### To dump data at a specified time, the app uses async `apscheduler` library that runs the dump function at a specified time interval.

### Dump command saves the data to a .csv file with datetime in a dumps/ directory.

## By default, the app will only dump the data to a csv file at a specified time, so the scraper needs to be launched manually.
## The dump example can be seen in [example_2026-02-06.csv](example_2026-02-06.csv) file.
## Scraping were done to the specific page https://auto.ria.com/uk/search/ with query parameters:
- `?search_type=2` - used cars only;
- `&page={page_num}` - page number, used to iterate over the pages;
- `&limit=100` - limit of cars on 1 page, to reduce the amount of requests to the website, the increased limit were used.

# How to run

### To launch the app, you need Docker installed.

## Then you need to copy the [.env.sample](.env.sample) file to .env and fill in the required fields or leave as is for local testing/development.

```bash
cp .env.sample .env
```

## After that we can build and launch the container:

```bash
docker-compose up -d --build
```


## Launch the scraper:

### For this we need to connect to the container and execute:

```bash
python -m app.main scrape
```

### Or the full command to connect and execute:

```bash
docker exec -it myapp python -m app.main scrape
```

#### If you want to launch the dump function manually as well, you need to change the command to:

```bash
docker exec -it myapp python -m app.main dump
```

#### Only the last command changes, so use `dump` to dump data and `scrape` to scrape data.
