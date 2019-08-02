using UnityEngine;
using System.Collections;

public class SendPositionOnUpdate : MonoBehaviour {

	public OSC osc;

	// Use this for initialization
	void Start () {
	
	}
	
	// Update is called once per frame
	void Update () {

	  OscMessage message = new OscMessage();

        message.address = "/UpdateXYZ";
        message.values.Add(transform.position.x);
        message.values.Add(transform.position.y);
        message.values.Add(transform.position.z);
        Debug.Log("update XYZ: " + transform.position.x);
        osc.Send(message);

        message = new OscMessage();
        message.address = "/UpdateX";
        message.values.Add(transform.position.x);
        Debug.Log("update X: " + transform.position.x);
        osc.Send(message);

        message = new OscMessage();
        message.address = "/UpdateY";
        message.values.Add(transform.position.y);
        Debug.Log("update Y: " + transform.position.x);
        osc.Send(message);

        message = new OscMessage();
        message.address = "/UpdateZ";
        message.values.Add(transform.position.z);
        Debug.Log("update Z: " + transform.position.x);
        osc.Send(message);


    }


}
