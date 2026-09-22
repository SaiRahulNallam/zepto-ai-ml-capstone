## q1_where

```sql
SELECT title, price_gbp FROM books WHERE rating >= 4 ORDER BY price_gbp DESC;
```

| title                                                                    |   price_gbp |
|:-------------------------------------------------------------------------|------------:|
| The No. 1 Ladies' Detective Agency (No. 1 Ladies' Detective Agency #1)   |       57.7  |
| A Year in Provence (Provence #1)                                         |       56.88 |
| The Past Never Ends                                                      |       56.5  |
| A Flight of Arrows (The Pathfinders #2)                                  |       55.53 |
| Murder at the 42nd Street Library (Raymond Ambler #1)                    |       54.36 |
| The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1) |       52.3  |
| Full Moon over Noahâs Ark: An Odyssey to Mount Ararat and Beyond       |       49.43 |
| A Time of Torment (Charlie Parker #14)                                   |       48.35 |
| Sharp Objects                                                            |       47.82 |
| The Murder of Roger Ackroyd (Hercule Poirot #4)                          |       44.1  |
| While You Were Mine                                                      |       41.32 |
| A Paris Apartment                                                        |       39.01 |
| The Red Tent                                                             |       35.66 |
| World Without End (The Pillars of the Earth #2)                          |       32.97 |
| Mrs. Houdini                                                             |       30.25 |
| The Passion of Dolssa                                                    |       28.32 |
| The Marriage of Opposites                                                |       28.08 |
| Lost Among the Living                                                    |       27.7  |
| 1,000 Places to See Before You Die                                       |       26.08 |
| What Happened on Beale Street (Secrets of the South Mysteries #2)        |       25.37 |
| The Mysterious Affair at Styles (Hercule Poirot #1)                      |       24.8  |
| The Silkworm (Cormoran Strike #2)                                        |       23.05 |
| Voyager (Outlander #3)                                                   |       21.07 |
| Delivering the Truth (Quaker Midwife Mystery #1)                         |       20.89 |
| Between Shades of Gray                                                   |       20.79 |
| A Spy's Devotion (The Regency Spies of London #1)                        |       16.97 |
| The Girl You Lost                                                        |       12.29 |

## q2_order_limit

```sql
SELECT title, price_inr FROM books ORDER BY price_inr DESC LIMIT 10;
```

| title                                                                  |   price_inr |
|:-----------------------------------------------------------------------|------------:|
| Boar Island (Anna Pigeon #19)                                          |     6275.14 |
| The No. 1 Ladies' Detective Agency (No. 1 Ladies' Detective Agency #1) |     6087.35 |
| A Year in Provence (Provence #1)                                       |     6000.84 |
| The Past Never Ends                                                    |     5960.75 |
| The Last Painting of Sara de Vos                                       |     5860.52 |
| A Flight of Arrows (The Pathfinders #2)                                |     5858.41 |
| Murder at the 42nd Street Library (Raymond Ambler #1)                  |     5734.98 |
| The Last Mile (Amos Decker #2)                                         |     5719.15 |
| 1st to Die (Women's Murder Club #1)                                    |     5694.89 |
| Tipping the Velvet                                                     |     5669.57 |

## q3_distinct

```sql
SELECT DISTINCT category FROM (SELECT c.category_name AS category FROM books b JOIN categories c ON b.category_id = c.category_id);
```

| category           |
|:-------------------|
| Travel             |
| Mystery            |
| Historical Fiction |

## q4_between

```sql
SELECT title, rating, price_gbp FROM books WHERE price_gbp BETWEEN 20 AND 40 ORDER BY price_gbp;
```

| title                                                                                             |   rating |   price_gbp |
|:--------------------------------------------------------------------------------------------------|---------:|------------:|
| Blood Defense (Samantha Brinkman #1)                                                              |        3 |       20.3  |
| Love, Lies and Spies                                                                              |        2 |       20.55 |
| Between Shades of Gray                                                                            |        5 |       20.79 |
| Delivering the Truth (Quaker Midwife Mystery #1)                                                  |        4 |       20.89 |
| Voyager (Outlander #3)                                                                            |        5 |       21.07 |
| The Silkworm (Cormoran Strike #2)                                                                 |        5 |       23.05 |
| The Road to Little Dribbling: Adventures of an American in Britain (Notes From a Small Island #2) |        1 |       23.21 |
| Career of Evil (Cormoran Strike #3)                                                               |        2 |       24.72 |
| The Mysterious Affair at Styles (Hercule Poirot #1)                                               |        4 |       24.8  |
| What Happened on Beale Street (Secrets of the South Mysteries #2)                                 |        5 |       25.37 |
| Extreme Prey (Lucas Davenport #26)                                                                |        3 |       25.4  |
| Starlark                                                                                          |        3 |       25.83 |
| 1,000 Places to See Before You Die                                                                |        5 |       26.08 |
| Girl With a Pearl Earring                                                                         |        1 |       26.77 |
| Poisonous (Max Revere Novels #3)                                                                  |        3 |       26.8  |
| The Widow                                                                                         |        2 |       27.26 |
| Lost Among the Living                                                                             |        4 |       27.7  |
| The Marriage of Opposites                                                                         |        4 |       28.08 |
| The Passion of Dolssa                                                                             |        5 |       28.32 |
| Forever and Forever: The Courtship of Henry Longfellow and Fanny Appleton                         |        3 |       29.69 |
| Mrs. Houdini                                                                                      |        5 |       30.25 |
| The Great Railway Bazaar                                                                          |        1 |       30.54 |
| World Without End (The Pillars of the Earth #2)                                                   |        4 |       32.97 |
| The Secret Healer                                                                                 |        3 |       34.56 |
| Most Wanted                                                                                       |        3 |       35.28 |
| The Red Tent                                                                                      |        5 |       35.66 |
| Vagabonding: An Uncommon Guide to the Art of Long-Term World Travel                               |        2 |       36.94 |
| The House by the Lake                                                                             |        1 |       36.95 |
| Under the Tuscan Sun                                                                              |        3 |       37.33 |
| The Invention of Wings                                                                            |        1 |       37.34 |
| In the Woods (Dublin Murder Squad #1)                                                             |        2 |       38.38 |
| Neither Here nor There: Travels in Europe                                                         |        3 |       38.95 |
| A Paris Apartment                                                                                 |        4 |       39.01 |

## q5_join

```sql
SELECT c.category_name AS category, b.title, b.rating, b.price_gbp FROM books b JOIN categories c ON b.category_id = c.category_id ORDER BY c.category_name, b.rating DESC, b.title LIMIT 30;
```

| category           | title                                                                     |   rating |   price_gbp |
|:-------------------|:--------------------------------------------------------------------------|---------:|------------:|
| Historical Fiction | A Flight of Arrows (The Pathfinders #2)                                   |        5 |       55.53 |
| Historical Fiction | A Spy's Devotion (The Regency Spies of London #1)                         |        5 |       16.97 |
| Historical Fiction | Between Shades of Gray                                                    |        5 |       20.79 |
| Historical Fiction | Mrs. Houdini                                                              |        5 |       30.25 |
| Historical Fiction | The Passion of Dolssa                                                     |        5 |       28.32 |
| Historical Fiction | The Red Tent                                                              |        5 |       35.66 |
| Historical Fiction | Voyager (Outlander #3)                                                    |        5 |       21.07 |
| Historical Fiction | While You Were Mine                                                       |        5 |       41.32 |
| Historical Fiction | A Paris Apartment                                                         |        4 |       39.01 |
| Historical Fiction | Lost Among the Living                                                     |        4 |       27.7  |
| Historical Fiction | The Marriage of Opposites                                                 |        4 |       28.08 |
| Historical Fiction | World Without End (The Pillars of the Earth #2)                           |        4 |       32.97 |
| Historical Fiction | Forever and Forever: The Courtship of Henry Longfellow and Fanny Appleton |        3 |       29.69 |
| Historical Fiction | Glory over Everything: Beyond The Kitchen House                           |        3 |       45.84 |
| Historical Fiction | Starlark                                                                  |        3 |       25.83 |
| Historical Fiction | The Constant Princess (The Tudor Court #1)                                |        3 |       16.62 |
| Historical Fiction | The Secret Healer                                                         |        3 |       34.56 |
| Historical Fiction | Girl in the Blue Coat                                                     |        2 |       46.83 |
| Historical Fiction | Lilac Girls                                                               |        2 |       17.28 |
| Historical Fiction | Love, Lies and Spies                                                      |        2 |       20.55 |
| Historical Fiction | The Last Painting of Sara de Vos                                          |        2 |       55.55 |
| Historical Fiction | Girl With a Pearl Earring                                                 |        1 |       26.77 |
| Historical Fiction | The Guernsey Literary and Potato Peel Pie Society                         |        1 |       49.53 |
| Historical Fiction | The House by the Lake                                                     |        1 |       36.95 |
| Historical Fiction | The Invention of Wings                                                    |        1 |       37.34 |
| Historical Fiction | Tipping the Velvet                                                        |        1 |       53.74 |
| Mystery            | A Time of Torment (Charlie Parker #14)                                    |        5 |       48.35 |
| Mystery            | The Bachelor Girl's Guide to Murder (Herringford and Watts Mysteries #1)  |        5 |       52.3  |
| Mystery            | The Girl You Lost                                                         |        5 |       12.29 |
| Mystery            | The Silkworm (Cormoran Strike #2)                                         |        5 |       23.05 |

