using UnityEngine;
using System.Collections;

public class ReceiveFilename0 : MonoBehaviour {
    
   	public OSC osc;

    // Use this for initialization
    void Start () {
	    osc.SetAddressHandler("/fname0" , OnReceivefname);
    }
	
	// Update is called once per frame
	void Update () {
	
	}

    void OnReceivefname(OscMessage message)
    {
        string fname = message.ToString();

        // cut off the extension, required by Unity
        int ext_pos = fname.LastIndexOf(".");
            
        if (ext_pos >= 0)
            fname = fname.Substring(0, ext_pos);
        fname = fname.Substring(8);
        Debug.Log(fname);

        AudioSource audio = GetComponent<AudioSource>();
        //var www = new WWW("C:\\Users\\Public\\Code\\unitycontroller\\" + fname);
        //AudioClip myAudioClip = www.audioClip;
        //while (!myAudioClip.isReadyToPlay)
        //    yield return www;
        AudioClip newclip = Resources.Load<AudioClip>(fname);
        Debug.Log("start of clip");
        Debug.Log(newclip);
        audio.clip = newclip;
        OscMessage reply;
        reply = new OscMessage();
        reply.address = "/loaded";
        reply.values.Add('1');
        osc.Send(reply);
    }
}
