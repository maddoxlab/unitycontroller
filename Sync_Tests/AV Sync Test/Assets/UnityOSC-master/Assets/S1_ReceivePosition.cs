using UnityEngine;
using System.Collections;

public class S1_ReceivePosition : MonoBehaviour {
    
   	public OSC osc;


	// Use this for initialization
	void Start () {
	   osc.SetAddressHandler("/Sphere1_PositionXYZ", OnReceiveXYZ );
       osc.SetAddressHandler("/Sphere1_PositionX", OnReceiveX);
       osc.SetAddressHandler("/Sphere1_PositionY", OnReceiveY);
       osc.SetAddressHandler("/Sphere1_PositionZ", OnReceiveZ);
    }
	
	// Update is called once per frame
	void Update () {
	
	}

	void OnReceiveXYZ(OscMessage message){
		float x = message.GetInt(0);
         float y = message.GetInt(1);
		float z = message.GetInt(2);

		transform.position = new Vector3(x,y,z);
	}

    void OnReceiveX(OscMessage message) {
        float x = message.GetFloat(0);

        Vector3 position = transform.position;

        position.x = x;

        transform.position = position;
    }

    void OnReceiveY(OscMessage message) {
        float y = message.GetFloat(0);

        Vector3 position = transform.position;

        position.y = y;

        transform.position = position;
    }

    void OnReceiveZ(OscMessage message) {
        float z = message.GetFloat(0);

        Vector3 position = transform.position;

        position.z = z;

        transform.position = position;
    }


}
