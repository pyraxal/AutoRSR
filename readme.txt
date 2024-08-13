Hello!

This is AutoRSR, a project written in order to leverage AI to automatically score for Redmond Sentence Recall (RSR). The goal of this is to implement a screening protocol that will eventually automate the screening of children.  

You can check out a working demo that implements this code at: https://aipipelines.xlabub.com/. If you want to run the code yourself, please follow the instructions below. 

-------------------------------------------------------------------------------------------

To use, please install and any dependencies:
Whisperx (https://github.com/m-bain/whisperX)
Whisper (https://huggingface.co/openai/whisper-large-v3)
FFmpeg (https://www.ffmpeg.org/)

If you have installed all the dependencies, you should only need to pip install ftfy. To use Auto_RSR, I would recommend using a conda environment as some dependencies are dependent on conda to run its best. You can hack out a solution with only a venv + pip environment, though it might be harder. 
-------------------------------------------------------------------------------------------

Additionally, please clone:
Bertalign (https://github.com/bfsujason/bertalign)

After cloning, install everything in requirements.txt in Bertalign. Then, in the aligner_py of Beralign-Main, please add this function after print_sents:

def return_sents(self):
        a_list = []
        for bead in (self.result):
            src_line = self._get_line(bead[0], self.src_sents)
            tgt_line = self._get_line(bead[1], self.tgt_sents)
            a_list.append(src_line + "\n")
            a_list.append(tgt_line + "\n")
        return a_list

Then, please modify bert.py included in the GitHub repo to include the location of where you placed your cloned bert repo. 
-------------------------------------------------------------------------------------------

After doing this, you are good to go! At the bottom any .py that can be used standalone have a sample included of how to use. If you just want to get straight to running AutoRSR, I would use batch_process.py. 