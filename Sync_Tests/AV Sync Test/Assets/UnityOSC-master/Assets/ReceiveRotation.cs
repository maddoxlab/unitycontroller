using UnityEngine;
using System.Collections;

public class ReceiveRotation : MonoBehaviour {
    
   	public OSC osc;


	// Use this for initialization
	void Start () {
	   osc.SetAddressHandler("/RotateXYZ" , OnReceiveXYZ );
       osc.SetAddressHandler("/RotateX", OnReceiveX);
       osc.SetAddressHandler("/RotateY", OnReceiveY);
       osc.SetAddressHandler("/RotateZ", OnReceiveZ);
    }
	
	// Update is called once per frame
	void Update () {
	
	}

	void OnReceiveXYZ(OscMessage message){
		float x = message.GetInt(0);
        float y = message.GetInt(1);
		float z = message.GetInt(2);
       
		transform.rotation = new Quaternion(x,y,z,360);
	}

    void OnReceiveX(OscMessage message) {
        float x = message.GetFloat(0);

        Quaternion rotation = transform.rotation;

        rotation.x = x;

        transform.rotation = rotation;
    }

    void OnReceiveY(OscMessage message) {
        float y = message.GetFloat(0);

        Quaternion rotation = transform.rotation;

        rotation.y = y;

        transform.rotation = rotation;
    }

    void OnReceiveZ(OscMessage message) {
        float z = message.GetFloat(0);

        Quaternion rotation = transform.rotation;

        rotation.z = z;
        transform.rotation = rotation;
    }


}
