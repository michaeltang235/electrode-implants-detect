This repository highlights some of the code I wrote for the project of automatic detection of electrode implants in the brain using techniques of computer vision. 

**Background:**\
For epilepsy patients, seizure freedom can be achieved by surgical removal of epileptic brain areas. The gold standard to identify these areas involves implanting electrodes into the brain during presurgical workup. Electrodes implanted allow direct measurement of seizure-related activity, yet it requires hours of extensive manual labor by MRI Technicians to mark the locations of electrodes in MR images, preventing them from working on other tasks that are equally important, for instance, administering MRI scans and providing patient care. Therefore, this project aims to develop an automatic detection algorithm that could reduce the time taken to register the locations of electrode implants from hours to minutes using techniques of computer vision.


**Progress:**\
We were able to identify locations of majority of electrode contacts using a reference template made by cropping 
images of electrode contacts. The general flowchart of the algorithm involes 4 steps, <br/>
step 1: remove ncc <= ncc threshold, here ncc refers to normalized cross correlation <br />
step 2: remove overlapping detections with nms, here nms stands for non-maximum suppression <br />
step 3: remove isolated detections <br />
step 4: select contacts that agreed with the geometry of an electrode (i.e. those that are collinear and equidistant from one another) <br />

Currently, we are working on the training data set to obtain a template that is most representative on all electrode contacts available. <br />
