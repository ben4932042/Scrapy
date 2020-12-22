# Overview

---

## Setup 
### For local development environment usage 
```bash
~$ cd ${project}
~$ scrapy crawl google_search
```
### For docker environment usage 
```bash
~$ docker pull ben0824/scrapy
~$ docker run -it --name googlesearch --env-file ./env ben0824/scrapy /bin/sh
```

#### Todos
- Implement Kubernetes environment setting
- Improve CI/CD
- 
#### Requirements
Scrapy is tested with:

|              | Master version (dev)      | 
| ------------ | ------------------------- |
| python       | 3.6            | 
| docker       | 20.10.0            | 


