# faster_rcnn-beverage_detector

Download model [here](https://drive.google.com/open?id=1FAziE7Zu_gQitGQxzPRpO10W_qjILMQM) and set them in the `tools/` folder.


Download pre-trained models and weights.
```
mkdir -p data/imagenet_weights
cd data/imagenet_weights
wget -v http://download.tensorflow.org/models/vgg_16_2016_08_28.tar.gz
tar -xzvf vgg_16_2016_08_28.tar.gz
mv vgg_16.ckpt vgg16.ckpt
cd ../..
```