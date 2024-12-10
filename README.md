
# <span style="color:blue">AmaZone</span>


## 💡About

ForestDeforestationSurvey is a comprehensive tool designed to help users monitor and analyze forested areas for signs of deforestation. Leveraging the power of Google Earth Engine for satellite imagery and a machine learning model for analysis, this project provides an automated and efficient way to assess forest health and detect changes over time.


## 🔀 Installation and imports
To clone the report

```https://github.com/tomvlt1/amazonev2```

Then navigate to the app folder within the Datastructures folder



 We have not yet made usable for other users as there are a lot of account linked access. For example, to use this someone would need to access my gmail account. As such, we have not made a requirements file as this isnt made to be shared and used by others as of yet (Work in progress)
## 💻 Usage



First run 
```
streamlit run ZoneSelect.py
```
This lets you choose an area (within the amazon forest) of a max radius of 1km
(change to come)

This will open a page, select an area and quit the page, no saving needed.



``` python3 main.py ```

or 

```python main.py```


This will connect to EE API (EarthEngine) 
and extract a satellite image. It then passes this image (after processing it) to the pretrained CNN from Teachable machine which has been fined tuned with a sample of ~500 photos that were manually collected.

The model will output a forest density percentage. Ranging from 0-100% in increments of 33.
(0,33,66,100).

_**DISCLAIMER**_: The accuracy of the model seems to be a little too high and perhaps something wrong with our training data or some overfitting.



## 📃 Authors

- [@tomvlt1](https://github.com/tomvlt1)
- [@guittoi](https://github.com/guittoi)

