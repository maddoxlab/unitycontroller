using UnityEngine;
using System.Collections;

public class ReceiveTest : MonoBehaviour {
    
   	public OSC osc;


	// Use this for initialization
	void Start () {
	   osc.SetAddressHandler( "/Test" , Test );
        Debug.Log("Init");
    }
	
	// Update is called once per frame
	void Update () {
      
	}

	void Test(OscMessage message){
        Debug.Log("Test: " + message);
    }


}
