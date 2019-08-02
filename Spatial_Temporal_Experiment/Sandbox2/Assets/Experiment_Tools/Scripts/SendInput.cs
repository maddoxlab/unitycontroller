using UnityEngine;
using System.Collections;

public class SendInput : MonoBehaviour {

    public OSC osc;
    public enum Hand { Right, Left };

    public Hand hand;
    private OVRInput.Button button_vis;
    private OVRInput.Button button_aud;
            

    void Start()
    {

        GameObject player = GameObject.Find("LocalAvatar");

        if (hand.Equals(Hand.Right))
        {
            button_vis = OVRInput.Button.One;
            button_aud = OVRInput.Button.Two;
        }
        else
        {
            button_vis = OVRInput.Button.Three;
            button_aud = OVRInput.Button.Four;
        }
    }


    void Update()
    {
    
        bool vis_pressed = OVRInput.Get(button_vis);
        bool aud_pressed = OVRInput.Get(button_aud);

        OscMessage reply;
        reply = new OscMessage();
        reply.address = "/response";
        if (vis_pressed | aud_pressed)
        {
            
            Debug.Log("you pressed the button");
            int vis = vis_pressed ? 1 : 0;
            int aud = aud_pressed ? 1 : 0;
            reply.values.Add(vis);
            reply.values.Add(aud);
            osc.Send(reply);
        }
    }

}

