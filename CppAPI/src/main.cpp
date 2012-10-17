#include <Windows.h>
#include <Winhttp.h>
#include <iostream>

#include "WebTics.h"

#pragma comment( lib,"Winhttp.lib")
#pragma comment( lib,"Winmm.lib")

/* Int to string */
string itos(int i)
{
    stringstream s;
    s << i;
    return s.str();
}

/* Double to string */
string dtos(double d)
{
    stringstream s;
    s << d;
    return s.str();
}
void duringRuntime()
{
    /* At any point you need to send metric then something like this*/
    /* get the WebTics Singleton*/
	WebTics *metricsSystem = WebTics::GetInstance();
    
	string result("");
    /* create a data string with values from the game */
    string dataToSend("");
    dataToSend.append("x=").append(itos(1)); 
   
    dataToSend.append("&y=").append(itos(2));
    dataToSend.append("&speedx=").append(dtos(3.f));

    /* send the message to the host and php path you initialised to earlier */
    metricsSystem->SendMessage(&dataToSend, &result);
    printf("%s\n\n", result.c_str());
}

int main(int argc,char** argv){ 

//    int i = GameMetricEvents::eventSubtypes::FALL;

	// reply string from PHP
	string result("");


	// setup with host URL and default php path
	WebTics *metricsSystem = WebTics::GetInstance();
    metricsSystem->Initialise(new string("localhost"), new string("/test/"));

    
	// hash sent, no reply required
	result.assign("No reply Needed");
	metricsSystem->SendMessage(new string("userhash=9eef6a1f927654f24801f58fe67bb1d4"));

    metricsSystem->SendMessage(new string("userhash=9eef6a1f927654f24801f58fe67bb1d"), &result, new string("/getUsers.php"));

	printf("%s\n\n", result.c_str());


    //duringRuntime();
    
    //metricsSystem->SetPHPPath(WebTics::PHPPathType::IS_AUTHORISED, new string("/isAuthorised_v2.0.php"));
    /*
    // ======== Two options, Initialise() and SetServer() both bet initialised to true
	//metricsSystem->Initialise(new string("localhost"), new string("/test/"));
    // OR
    //metricsSystem->SetServer(new string("localhost"));
    metricsSystem->SetPath(new string("/test/getUsers.php"));
    // ========

	// send an message with no
	metricsSystem->SendMessage(new string(""), &result);
	printf("%s\n\n", result.c_str());

	// hash sent
	metricsSystem->SendMessage(new string("userhash=9eef6a1f927654f24801f58fe67bb1d"), &result, new string("/getUsers.php"));
	printf("%s\n\n", result.c_str());
    */
    

	// use a different php file, no reply required
	metricsSystem->SendMessage(new string("userhash=9eef6a1f927654f24801f58fe67bb1d4"), NULL, new string("/test/getMessages.php"));




	printf("%s\n\n", result.c_str());
    
    system("pause");
    return 0;
}