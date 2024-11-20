This repository highlights some of the code I wrote for the project of automatic detection of electrode implants in the brain using techniques of computer vision. 

**Background:**\
For epilepsy patients, seizure freedom can be achieved by surgical removal of epileptic brain areas. The gold standard to identify these areas involves implanting electrodes into the brain during presurgical workup. Electrodes implanted allow direct measurement of seizure-related activity, yet it requires hours of extensive manual labor by MRI Technicians to mark the locations of electrodes in MR images, preventing them from working on other tasks that are equally important, for instance, administering MRI scans and providing patient care. Therefore, this project aims to develop an automatic detection algorithm that could reduce the time taken to register the locations of electrode implants from hours to minutes using techniques of computer vision.


**Progress:**\
We were able to identify locations of majority of electrode contacts using a reference template made by cropping 
images of electrode contacts. The general flowchart of the algorithm involes 4 steps, <br/>

step 1: manually create reference template, then aligned all images of electrode contacts in the dataset with reference template to create average 3d template (w_1) <br />
step 2: translate w_1 across anatomical image in x, y, and z directions to obtain a 3d array of normalized cross correlation (ncc). <br />
step 2_1: remove tranlations with ncc <= ncc threshold (only those voxels of high similarity to template would have high enough ncc value) <br />
step 2_2: remove overlapping detections with non-maximum suppression  <br />
step 2_3: remove isolated detections <br />
step 3: select contacts that agreed with the geometry of an electrode (i.e. those that are collinear and equidistant from one another) <br />
step 4: compare electrodes and their contacts identified by the algorithm with dataset, and generate summary of the performance of the algorithm, which includes
the following: <br />

no. of electrodes in dataset <br />
no. of elect. with contacts detected  <br />
no. of elect. with no contacts detected  <br />
no. of comb. found  <br />
no. of comb. found with no matched elect. in dataset <br />
no. of contacts detected  <br />
no. of contacts in dataset ---(A)  <br />
no. of true positives ---(B)  <br />
no. of false positives ---(C)  <br />
B/A  <br /> 
C/A  <br />


Currently, we are working on thw following: <br />
-obtaining a template in the training dataset that is most representative on all electrode contacts available <br />
-adding a feature of intensity (min., max., avg.) to filter out false detection candidates <br />
