import sys
sys.path.insert(0, '.')
from mini_run_pipeline.subject_placement import observe_subject

obs = observe_subject('remotion-app/public/source/test-video.mp4', 30000)
for f in obs.get('frames', [])[:5]:
    fb = f.get('faceBox')
    sb = f.get('subjectBox')
    print("Frame:", f.get('sourceMs'), "face:", fb, "subject:", sb)
