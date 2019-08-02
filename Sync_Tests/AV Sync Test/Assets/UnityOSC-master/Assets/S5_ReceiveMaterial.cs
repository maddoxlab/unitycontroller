using UnityEngine;
using System.Collections;

public class S5_ReceiveMaterial : MonoBehaviour {
    
   	public OSC osc;

    // Use this for initialization
    void Start () {
	    osc.SetAddressHandler("/Sphere5_Color" , OnReceiveColor);
        osc.SetAddressHandler("/Sphere5_Alpha", OnReceiveAlpha);
        osc.SetAddressHandler("/Sphere5_Visible", OnReceiveVisible);
    }
	
	// Update is called once per frame
	void Update () {
	
	}

	void OnReceiveColor(OscMessage message){
		float r = message.GetFloat(0);
        float g = message.GetFloat(1);
		float b = message.GetFloat(2);
        float a = message.GetFloat(3);
        this.GetComponent<Renderer>().material.SetColor("_Color", new Vector4(r, g, b, a));
    }

    void OnReceiveAlpha(OscMessage message){
        float a = message.GetFloat(0);
        Color color = this.GetComponent<Renderer>().material.GetColor("_Color");
        color.a = a;
        this.GetComponent<Renderer>().material.SetColor("_Color", color);
    }

    void OnReceiveVisible(OscMessage message){
        int int_v = message.GetInt(0);
        if (int_v == 1)
        {
            this.GetComponent<Renderer>().enabled = true;
        }
        else
        {
            this.GetComponent<Renderer>().enabled = false;
        }
    }       
}
