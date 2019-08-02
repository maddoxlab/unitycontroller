using UnityEngine;
using System.Collections;

public class ReceiveScale : MonoBehaviour {
    
   	public OSC osc;


	// Use this for initialization
	void Start () {
	   osc.SetAddressHandler("/ScaleXYZ" , OnReceiveXYZ );
       osc.SetAddressHandler("/ScaleX", OnReceiveX);
       osc.SetAddressHandler("/ScaleY", OnReceiveY);
       osc.SetAddressHandler("/ScaleZ", OnReceiveZ);
    }
	
	// Update is called once per frame
	void Update () {
	
	}

	void OnReceiveXYZ(OscMessage message){
		float x = message.GetFloat(0);
        float y = message.GetFloat(1);
		float z = message.GetFloat(2);
     
		transform.localScale = new Vector3(x,y,z);
	}

    void OnReceiveX(OscMessage message) {
        float x = message.GetFloat(0);

        Vector3 localScale = transform.localScale ;

        localScale.x = x;

        transform.localScale = localScale;
    }

    void OnReceiveY(OscMessage message) {
        float y = message.GetFloat(0);

        Vector3 localScale = transform.localScale;

        localScale.y = y;
        transform.localScale = localScale;
    }

    void OnReceiveZ(OscMessage message) {
        float z = message.GetFloat(0);

        Vector3 localScale = transform.localScale;

        localScale.z = z;

        transform.localScale = localScale;
    }


}
