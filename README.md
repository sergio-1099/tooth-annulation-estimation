# tooth-annulation-estimation

## annulation-estimation

Application with GUI that allows users to input an image or folder of images to estimate the number of annulations in teeth. Uses a Sequential model from Keras. The application will return a CSV if a folder was inputted with the filename, annulation estimate, and confidence of annulation region detection which was another model trained with RoboFlow:

https://app.roboflow.com/research-and-projects/annulation-region-detection/1

## annulation-detection

This is a sub-application which is still independent from the original application, but detects annulation regions with a specific threshold that is chosen by the user. It can then annotate the images and save them to another folder. This is useful as it allows images to be separated for training purposes in the future.

## How to Use:

Both apps can be found in the Releases part of this GitHub.

### How To: annulation estimation

- Download Annulation.Apps.zip.
- Open annulation estimation executable (may need to configure settings or try more than once).
- Choose a folder or file.
- Choose the respective prediction button.
- If a folder is chosen and the Predict Folder button is chosen, another popup will come up asking to choose a save directory for the CSV file that will be created.
- If a file is chosen and the Predict File button is chosen, the information will be displayed in the GUI terminal.

### How To: annulation detection

- Download Annulation.Apps.zip.
- Open annulation detection executable.
- Choose a folder or file.
- Configure your threshold.
- Choose respective process button.
- If folder was processed, images will appear on the left with the terminal showing progress. Just one file can be processed as well, it will appear on the left with the terminal showing the process.
- Both options will give the user the ability to save images to a chosen directory.
- Click Restart to clear selections and images on the left.

## Jupyter Notebook Notes

The Jupyter Notebook in the GitHub repo is where the code I used to create and train the model is located. It also contains notes and explanations for some of the things I learned while creating this project. It also has some analysis and statistics of the performance of the model. It is there for reference purposes and the API key for RoboFlow has been removed. Be sure to create your own account if interested in using that software.

## Where to take this?

Some future ideas could include:

- Using different models that could perform better than the Sequential model from Keras.
- Use new data from a similar time frame of the training data to see more accurate results on performance.
- Improve GUI.
