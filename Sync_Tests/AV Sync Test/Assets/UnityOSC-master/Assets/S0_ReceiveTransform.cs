using UnityEngine;
using System.Collections;

public class S0_ReceiveTransform : MonoBehaviour {
    
   	public OSC osc;


	// Use this for initialization
	void Start () {
	    osc.SetAddressHandler("/Sphere0_PositionXYZ", OnReceivePosXYZ );
        osc.SetAddressHandler("/Sphere0_PositionX", OnReceivePosX);
        osc.SetAddressHandler("/Sphere0_PositionY", OnReceivePosY);
        osc.SetAddressHandler("/Sphere0_PositionZ", OnReceivePosZ);
        osc.SetAddressHandler("/Sphere0_RotateXYZ", OnReceiveRotXYZ);
        osc.SetAddressHandler("/Sphere0_RotateX", OnReceiveRotX);
        osc.SetAddressHandler("/Sphere0_RotateY", OnReceiveRotY);
        osc.SetAddressHandler("/Sphere0_RotateZ", OnReceiveRotZ);
        osc.SetAddressHandler("/Sphere0_ScaleXYZ", OnReceiveScaXYZ);
        osc.SetAddressHandler("/Sphere0_ScaleX", OnReceiveScaX);
        osc.SetAddressHandler("/Sphere0_ScaleY", OnReceiveScaY);
        osc.SetAddressHandler("/Sphere0_ScaleZ", OnReceiveScaZ);
    }
	
	// Update is called once per frame
	void Update () {
	
	}

	void OnReceivePosXYZ(OscMessage message){
		float x = message.GetFloat(0);
         float y = message.GetFloat(1);
		float z = message.GetFloat(2);

		transform.position = new Vector3(x,y,z);
	}

    void OnReceivePosX(OscMessage message) {
        float x = message.GetFloat(0);

        Vector3 position = transform.position;

        position.x = x;

        transform.position = position;
    }

    void OnReceivePosY(OscMessage message) {
        float y = message.GetFloat(0);

        Vector3 position = transform.position;

        position.y = y;

        transform.position = position;
    }

    void OnReceivePosZ(OscMessage message) {
        float z = message.GetFloat(0);

        Vector3 position = transform.position;

        position.z = z;

        transform.position = position;
    }

    void OnReceiveRotXYZ(OscMessage message)
    {
        float x = message.GetInt(0);
        float y = message.GetInt(1);
        float z = message.GetInt(2);

        transform.rotation = new Quaternion(x, y, z, 360);
    }

    void OnReceiveRotX(OscMessage message)
    {
        float x = message.GetFloat(0);

        Quaternion rotation = transform.rotation;

        rotation.x = x;

        transform.rotation = rotation;
    }

    void OnReceiveRotY(OscMessage message)
    {
        float y = message.GetFloat(0);

        Quaternion rotation = transform.rotation;

        rotation.y = y;

        transform.rotation = rotation;
    }

    void OnReceiveRotZ(OscMessage message)
    {
        float z = message.GetFloat(0);

        Quaternion rotation = transform.rotation;

        rotation.z = z;
        Debug.Log("Quat: " + rotation.w);
        transform.rotation = rotation;
    }

    void OnReceiveScaXYZ(OscMessage message)
    {
        float x = message.GetFloat(0);
        float y = message.GetFloat(1);
        float z = message.GetFloat(2);

        transform.localScale = new Vector3(x, y, z);
    }

    void OnReceiveScaX(OscMessage message)
    {
        float x = message.GetFloat(0);

        Vector3 localScale = transform.localScale;

        localScale.x = x;

        transform.localScale = localScale;
    }

    void OnReceiveScaY(OscMessage message)
    {
        float y = message.GetFloat(0);

        Vector3 localScale = transform.localScale;

        localScale.y = y;
        transform.localScale = localScale;
    }

    void OnReceiveScaZ(OscMessage message)
    {
        float z = message.GetFloat(0);

        Vector3 localScale = transform.localScale;

        localScale.z = z;

        transform.localScale = localScale;
    }

}
