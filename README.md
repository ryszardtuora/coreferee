# coreferencer


```bash
docker build . -t coreferencer
docker run -it coreferencer
```

```
>>> import coreferencer, spacy
>>> nlp = spacy.load('pl_core_news_lg')
>>> nlp.add_pipe('coreferencer')
<coreferencer.manager.CoreferencerBroker object at 0x0000027304C63B50>
>>>
>>> doc = nlp("Właściciele skupu wiele robią dla środowiska, ale to jest ich praca. Muszą też zarobić, a to opłaca się coraz mniej.")
>>>
>>> doc._.coref_chains.print()
>>>
>>> doc._.coref_chains.resolve(doc[27])
>>>
```
