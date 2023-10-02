This repository highlights some of the code I wrote for the project of automatic detection of electrode implants in the brain using techniques of computer vision. 

**Background:**\
For epilepsy patients, seizure freedom can be achieved by surgical removal of epileptic brain areas. The gold standard to identify these areas involves implanting electrodes into the brain during presurgical workup. Electrodes implanted allow direct measurement of seizure-related activity, yet it requires hours of extensive manual labor by MRI Technicians to mark the locations of electrodes in MR images, preventing them from working on other tasks that are equally important, for instance, administering MRI scans and providing patient care. Therefore, this project aims to develop an automatic detection algorithm that could reduce the time taken to register the locations of electrode implants from hours to minutes using techniques of computer vision.


**Progress:**\
We were able to identify locations of majority of electrode contacts using a reference template made by cropping 
images of electrode contacts. The general flowchart of the algorithm involes 3 steps, 
step 1: remove ncc <= ncc threshold, here ncc refers to normalized cross correlation
step 2: remove overlapping detections with nms, here nms stands for non-maximum suppression
step 3: remove isolated detections

Currently, we are working on using a multi-contact template to remove false positives by incorporating the following features of electrode contacts into the algorithm,
1) contacts detected have to form a straight line, as they can only be found on electrodes (straight needles) implanted
2) allow rotation of templates in 3D to search for best match
