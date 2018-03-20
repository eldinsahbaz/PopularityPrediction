# PopularityPrediction
Predict the popularity of videos at the time of upload

# Update <11/2017>
Currently reworking solution. [CollectData.py](https://github.com/eldinsahbaz/VideoPopularity/blob/master/new/CollectData.py) contains code for a more methodical approach to sampling videos and collecting data. This approach to sampling introduces less bias and provides a better representation of the YouTube network than my previous approach. Still working on storing only processed audio data, rather than entire wav file (wav files tend to be very large). [Dataset](https://drive.google.com/file/d/1k6IWXeL_T_lngPzb8vwcPxZXWJ_Tib1F/view?usp=sharing)

# Update <8/2017>
This entire pipeline (data collection, processing, classification) is compressed into [Pipeline.py](https://github.com/eldinsahbaz/VideoPopularity/blob/master/old/Pipeline.py) (currently undocumented). [Dataset](https://drive.google.com/drive/folders/0B7MeMtrGJAEhbnhLZWVJOVN1UlE?usp=sharing)
