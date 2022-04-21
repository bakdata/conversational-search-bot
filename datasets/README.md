# Datasets

[Book dataset](http://www.cs.cmu.edu/~dbamman/booksummaries.html) (David Bamman and Noah Smith (2013), "New Alignment Methods for Discriminative Book Summarization")

[Movie dataset](https://www.kaggle.com/stefanoleone992/imdb-extensive-dataset?select=IMDb+movies.csv) (movies and ratings)

To index the data in elasticsearch run the [notebook](./create_elastic_jsons.ipynb).

POST the resulting .json files against your ES (indices are called 'movie', 'book', 'rating'):

```shell
curl -X POST -H "Content-Type: application/json" -d @movies.json localhost:9200/movie/_bulk
```
