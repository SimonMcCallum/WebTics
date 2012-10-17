#include <Windows.h>
#include <Winhttp.h>
#include <iostream>
#include <string>

#include "WebTics.h"
#include "WebTicsDefines.h"

using namespace std;


WebTics* WebTics::_instance = NULL;


/* ------------------------------------------------------------
 *
 *  Default path values for the system, these can be altered
 *
 ------------------------------------------------------------ */
const string* WebTics::defaultServer      = new string("localhost");
const string* WebTics::defaultPath        = new string("/WebTics/");

string* WebTics::openMetricSessionPHP     = new string("/openMetricSession.php");
string* WebTics::closeMetricSessionPHP    = new string("/closeMetricSession.php");
string* WebTics::registerEventsPHP        = new string("/registerEvents.php");
string* WebTics::startPlaySessionPHP      = new string("/startPlaySession.php");
string* WebTics::stopPlaySessionPHP       = new string("/stopPlaySession.php");
string* WebTics::requestParametersPHP     = new string("/requestParameters.php");
string* WebTics::logEventPHP              = new string("/logEvent.php");
string* WebTics::isAuthorisedPHP          = new string("/isAuthorised.php");
string* WebTics::setAuthorisedPHP         = new string("/setAuthorised.php");


#ifdef _DEBUG
    bool WebTics::debugMode = true;
#elif
    bool WebTics::debugMode = false;
#endif

/* ------------------------------------------------------------
 *
 *  Public access for the Singleton
 *
 ------------------------------------------------------------ */
WebTics* WebTics::GetInstance(bool autoInitialise)
{
	if (_instance == NULL)
	{
		_instance = new WebTics(autoInitialise);
	}
	return _instance;
};

/* ------------------------------------------------------------
 *
 *  Protected constructor
 *  autoInitialise (default = true) uses the default paths
 *    for server and base php path
 *
 ------------------------------------------------------------ */
WebTics::WebTics(bool autoInitialise)
{
    if (autoInitialise)
    {
        Initialise(defaultServer, defaultPath);
    	initialised = true;
    }
    else
    {
    	initialised = false;
    }
    metricSessionOpen = false;
};

/* ------------------------------------------------------------
 *
 *  Protected constructor
 *  autoInitialise (default = true) uses the default paths
 *    for server and base php path
 *
 ------------------------------------------------------------ */
WebTics::~WebTics()
{
	// Nothing dynamic allocated
	delete[] server;
	delete[] basepath;
};


/* ------------------------------------------------------------
 *
 *  Private Utility function to construct result string
 *    when an error occurs
 *
 ------------------------------------------------------------ */
void WebTics::setResultString(string* result, const char* part1, bool useError, const char* part2)
{
	result->append(part1);
	if (useError)
	{
		char error[8];
		sprintf_s(error, "%u%", GetLastError());
		result->append(error);
	}
	result->append(part2);
};

/* ------------------------------------------------------------
 *
 *  Public worker method, generic message sending
 *  used by all other message sending methods in the API
 *  May be private later
 *
 ------------------------------------------------------------ */
bool WebTics::SendMessage(string* urlData, string *result, string* urlPath)
{
	
	string returnValue("");
	wstring data(L"");
	wstring path(L"");
	wstring totalPath;
	bool errorStatus = true;

	if (!initialised)
	{
		setResultString(result, "WebTics::SendMessage Error ", false, ": WebTics not initialised");
		errorStatus = false;
		goto cleanupAndReturn;
	}

	/* initialise the rest to things needed */
	DWORD dwSize = 0;
	DWORD dwDownloaded = 0;
	LPSTR pszOutBuffer;
	BOOL  bResults = FALSE;
	HINTERNET   hSession = NULL, 
				hConnect = NULL,
				hRequest = NULL;
	
	if (urlData)
	{
		data.assign(urlData->begin(), urlData->end());
	}
	if(urlPath)
	{
		path.assign(urlPath->begin(), urlPath->end());
	}
	
	if (result != NULL)
	{
		result->assign("");
	}

	// Use WinHttpOpen to obtain a session handle.
	hSession = WinHttpOpen( L"WinHTTP Example/1.0",  
							WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
							WINHTTP_NO_PROXY_NAME, 
							WINHTTP_NO_PROXY_BYPASS, 
							WINHTTP_FLAG_ASYNC  );
	

	/*    ----------------------    */
	/*    Specify an HTTP server    */
	/*    ----------------------    */
	if( !hSession )
	{
		setResultString(result, "WebTics::SendMessage Error ", true, " in WinHttpOpen()");
		errorStatus = false;
		goto cleanupAndReturn;
	}
	else
	{
        //printf("%s\n", server->c_str());
		hConnect = WinHttpConnect(  hSession, server->c_str(), INTERNET_DEFAULT_HTTP_PORT, 0 );
	}
	

	/*    -----------------------------    */
	/*    Create an HTTP request handle    */
	/*    -----------------------------    */
	totalPath.assign(L"");
    totalPath.append(basepath->c_str());
	if (path.length() > 0)
	{
		totalPath.append(path.c_str());
	}
	if (data.length() > 0)
	{
		totalPath.append(L"?");
		totalPath.append(data.c_str());
	}


	/*    -----------------    */
	/*    open a connection    */
	/*    -----------------    */
	if( hConnect )
	{
		hRequest = WinHttpOpenRequest(  hConnect, L"GET", totalPath.c_str(),
										NULL, WINHTTP_NO_REFERER, 
										WINHTTP_DEFAULT_ACCEPT_TYPES, 
										0 );
	}
	

	/*    ----------------    */
	/*    send the request    */
	/*    ----------------    */
	if (!hRequest)
	{
		setResultString(result, "WebTics::SendMessage Error: ", true, " in WinHttpSendRequest()");
		errorStatus = false;
		goto cleanupAndReturn;
	}
	else // ( hRequest )
	{
		bResults = WinHttpSendRequest(  hRequest,
										WINHTTP_NO_ADDITIONAL_HEADERS, -1L,
										WINHTTP_NO_REQUEST_DATA, 0, 
										0, 
										NULL );
	}

	if (!bResults)
	{
		setResultString(result, "WebTics::SendMessage Error:", true, " in WinHttpSendRequest()");
		errorStatus = false;
		goto cleanupAndReturn;
	}
    

	/*    ---------------    */
	/*    No reply needed    */
	/*    ---------------    */
	if (result == NULL)
	{
		goto cleanupAndReturn;
	}
	

	/*    ---------------    */
	/*    receive a reply    */
	/*    ---------------    */
	if( bResults )
	{
		bResults = WinHttpReceiveResponse( hRequest, NULL );
	}

    // Response failed
    if( !bResults )
    { 
        setResultString(result, "WebTics::SendMessage Error: ", true, " in WinHttpReceiveResponse()");
		errorStatus = false;
		goto cleanupAndReturn;
    }
	// Keep checking for data until there is nothing left.
	else // ( bResults )
	{
		do 
		{
			// Check for available data.
			dwSize = 0;
			if( !WinHttpQueryDataAvailable( hRequest, &dwSize ) )
			{
		        setResultString(result, "WebTics::SendMessage Error: ", true, " in WinHttpQueryDataAvailable()");
				errorStatus = false;
				goto cleanupAndReturn;
			}

			// Allocate space for the buffer.
			pszOutBuffer = new char[dwSize+1];
                        
            // if the buffer failed to allocate
			if( !pszOutBuffer )
			{
		        setResultString(result, "WebTics::SendMessage Error: ", false, " Out of memory");
				errorStatus = false;
				goto cleanupAndReturn;
			}
            // A zero length buffer when a response was expected is an error
			else if( dwSize == 0 )
			{
		        setResultString(result, "WebTics::SendMessage Error: ", false, " Zero length response received");
				errorStatus = false;
				goto cleanupAndReturn;
			}
			else
			{
				// Read the data.
				ZeroMemory( pszOutBuffer, dwSize+1 );

				if( !WinHttpReadData( hRequest, 
									  (LPVOID)pszOutBuffer, 
									   dwSize,
									   &dwDownloaded ) )
				{
		            setResultString(result, "WebTics::SendMessage Error:", true, " in WinHttpReadData()");
					errorStatus = false;
					goto cleanupAndReturn;
				}
				else
				{			
					if (result != NULL)
					{
						result->assign(pszOutBuffer, MetricResultSize);
					}
					delete [] pszOutBuffer;
					goto cleanupAndReturn;
				}
			}
		} while( dwSize > 0 );
	}

	/*    ---------------------    */
	/*    report unknown errors    */
	/*    ---------------------    */
	if( !bResults )
	{
		if (result != NULL)
		{
		    setResultString(result, "WebTics::SendMessage Error: General WinHttp Error ", true, " has occurred");
			errorStatus = false;
			goto cleanupAndReturn;
		}
	}
		
cleanupAndReturn:
	// Close any open handles.
	if( hRequest ) WinHttpCloseHandle( hRequest );
	if( hConnect ) WinHttpCloseHandle( hConnect );
	if( hSession ) WinHttpCloseHandle( hSession );
	return errorStatus;
};



/* ------------------------------------------------------------
 *
 *  External API calls
 *      Initialise()
 *      SetServer()
 *      SetPath()
 *      OpenMetricSession()
 *      CloseMetricSession()
 *      RegisterEvents()
 *      IsAuthorised()
 *      SetAuthorised()
 *      RequestParameters()
 *      StartPlaySession()
 *      StopPlaySession()
 *      LogEvent() - with variations
 *
 ------------------------------------------------------------ */

 
/* ------------------------------------------------------------
 *
 *  Protected constructor
 *  autoInitialise (default = true) uses the default paths
 *    for server and base php path
 *
 ------------------------------------------------------------ */
void WebTics::Initialise(const string* server, const string* path)
{
	SetServer(server);
	SetPath(path);
};

/* ------------------------------------------------------------
 *
 *  Public function to set the metrics server address
 *  System is flagged as initialised after a server is set
 *
 ------------------------------------------------------------ */
void WebTics::SetServer(const string* server)
{
	this->server = new wstring(server->length(), L' ');
	copy(server->begin(), server->end(), this->server->begin());
	initialised = true;
};

/* ------------------------------------------------------------
 *
 *  Public function to set the base path of the 
 *    metrics PHP folder
 *
 ------------------------------------------------------------ */
void WebTics::SetPath(const string* path)
{
    if (path == NULL)
    {
        this->basepath = new wstring(0, L' ');
    }
    else
    {
    	this->basepath = new wstring(path->length(), L' ');
	    copy(path->begin(), path->end(), this->basepath->begin());
    }
};


void WebTics::OpenMetricSession(const string uniqueID)
{
    if (!metricSessionOpen)
    {
        string url("?id=");
        url.append(uniqueID);
        SendMessage(&url, &metricSessionMD5, const_cast<string *>(openMetricSessionPHP) );
        startTime = timeGetTime();
        metricSessionOpen = true;
    }
};
void WebTics::CloseMetricSession()
{
    if (metricSessionOpen)
    {
        SendMessage(&metricSessionMD5, NULL, const_cast<string *>(closeMetricSessionPHP) );
        metricSessionOpen = false;
    }
};


void WebTics::RegisterEvents()
{
    #pragma warning(push)
    #pragma warning(disable : 4482)

    if (!metricSessionOpen)
        return;

    string url("");
    string version("?v=");
    version.append(WebTicsDefines::versionLabel);
    for(int i = 0; i < WebTicsDefines::eventTypes::MAX_EVENT_TYPES; ++i)
    {
        url.append(version);
        url.append("&ev=").append(itos(i));
        url.append("&name=").append(WebTicsDefines::eventTypeNames[i]);

        SendMessage(&url, NULL, const_cast<string *>(registerEventsPHP) );
    }

    for(int i = 0; i < WebTicsDefines::eventSubtypes::MAX_EVENT_SUBTYPES; ++i)
    {
        url.append(version);
        url.append("&subev=").append(itos(i));
        url.append("&name=").append(WebTicsDefines::eventSubtypeNames[i]);

        SendMessage(&url, NULL, const_cast<string *>(registerEventsPHP) );
    }
    
    #pragma warning(pop)
};

bool WebTics::IsAuthorised(const string uniqueID)
{
    string result("");
    string url("?id=");
    url.append(uniqueID);

    SendMessage(&url, &result, const_cast<string *>(isAuthorisedPHP) );

    if (result.compare("true") == 0)
    {
        return true;
    }
    return false;
};
void WebTics::SetAuthorised(const string uniqueID, bool auth)
{
    string url("?id=");
    url.append(uniqueID);
    url.append("&auth=").append(auth?"true":"false");

    SendMessage(&url, NULL, const_cast<string *>(isAuthorisedPHP) );
};    


void WebTics::StartPlaySession()
{
    if (!metricSessionOpen)
        return;

    SendMessage(&metricSessionMD5, &playSessionMD5, const_cast<string *>(startPlaySessionPHP) );
};
void WebTics::StopPlaySession()
{
    if (!metricSessionOpen)
        return;

    SendMessage(&metricSessionMD5, NULL, const_cast<string *>(stopPlaySessionPHP) );
};

string* WebTics::RequestParameters(string* data)
{
    if (!metricSessionOpen)
        return NULL;

    string* result = new string("");
    if (data != NULL)
    {
        SendMessage(data, result, const_cast<string *>(requestParametersPHP) );
    }

    return result;
};

void WebTics::LogEvent(int type, int subtype, int x, int y, int z, double magnitude, string* data)
{
    if (!metricSessionOpen)
        return;

    string url("?");
    url.append("tick=").append(itos(timeGetTime()-startTime)); 
    url.append("&et=").append(itos(type)); 
    url.append("&est=").append(itos(subtype));
    url.append("&x=").append(itos(x));
    url.append("&y=").append(itos(y));
    url.append("&z=").append(itos(z));
    url.append("&m=").append(dtos(magnitude));
    if ((data != NULL) && (data->length() > 0))
    {
        url.append("&data=").append(data->c_str());
    }
    SendMessage(&url, NULL, const_cast<string *>(logEventPHP) );
};
void WebTics::LogEvent(int type, int subtype, int x, int y, int z, double magnitude)
{
    LogEvent(type, subtype, x, y, z, magnitude, NULL);
};
void WebTics::LogEvent(int type, int subtype, int x, int y, int z)
{
    LogEvent(type, subtype, x, y, z, 0, NULL);
};
void WebTics::LogEvent(int type, int subtype, double magnitude)
{
    LogEvent(type, subtype, 0, 0, 0, magnitude, NULL);
};
void WebTics::LogEvent(int type, int x, int y, int z)
{
    LogEvent(type, 0, x, y, z, 0, NULL);
};
void WebTics::LogEvent(int type, double magnitude)
{
    LogEvent(type, 0, 0, 0, 0, magnitude, NULL);
};
void WebTics::LogEvent(int type, string* data)
{
    LogEvent(type, 0, 0, 0, 0, 0.0, data);
};

void WebTics::SetDebugMode(bool mode)
{
    debugMode = mode;
}
void WebTics::LogEventDebug(int type, int subtype, int x, int y, int z, double magnitude, string* data)
{
    if (debugMode)
    {
        LogEvent(type, subtype, x, y, z, magnitude, data);
    }
}
void WebTics::LogEventDebug(int type, int subtype, int x, int y, int z, double magnitude)
{
    if (debugMode)
    {
        LogEvent(type, subtype, x, y, z, magnitude, NULL);
    }
}
void WebTics::LogEventDebug(int type, int subtype, int x, int y, int z)
{
    if (debugMode)
    {
        LogEvent(type, subtype, x, y, z, 0.f, NULL);
    }
}
void WebTics::LogEventDebug(int type, int subtype, double magnitude)
{
    if (debugMode)
    {
        LogEvent(type, subtype, 0, 0, 0, magnitude, NULL);
    }
}
void WebTics::LogEventDebug(int type, int x, int y, int z)
{
    if (debugMode)
    {
        LogEvent(type, 0, 0, 0, 0, 0.f, NULL);
    }
}
void WebTics::LogEventDebug(int type, double magnitude)
{
    if (debugMode)
    {
        LogEvent(type, 0, 0, 0, 0, magnitude, NULL);
    }
}
void WebTics::LogEventDebug(int type, string* data)
{
    if (debugMode)
    {
        LogEvent(type, 0, 0, 0, 0, 0.0, data);
    }
};

/* ------------------------------------------------------------
 *
 *  Public functions to update API paths
 *
 ------------------------------------------------------------ */
void WebTics::SetPHPPath(PHPPathType pathID, const string* newPath)
{
    #pragma warning(push)
    #pragma warning(disable : 4482)

    switch(pathID)
    {
    case PHPPathType::OPEN_METRIC_SESSION:
        openMetricSessionPHP->assign(newPath->c_str());
        break;
    case PHPPathType::CLOSE_METRIC_SESSION:
        closeMetricSessionPHP->assign(newPath->c_str());
        break;
    case PHPPathType::REGISTER_EVENTS:
        registerEventsPHP->assign(newPath->c_str());
        break;
    case PHPPathType::START_PLAY_SESSION:
        startPlaySessionPHP->assign(newPath->c_str());
        break;
    case PHPPathType::STOP_PLAY_SESSION:
        stopPlaySessionPHP->assign(newPath->c_str());
        break;
    case PHPPathType::REQUEST_PARAMETERS:
        requestParametersPHP->assign(newPath->c_str());
        break;
    case PHPPathType::LOG_EVENT:
        logEventPHP->assign(newPath->c_str());
        break;
    case PHPPathType::IS_AUTHORISED:
        isAuthorisedPHP->assign(newPath->c_str());
        break;
    case PHPPathType::SET_AUTHORISED:
        setAuthorisedPHP->assign(newPath->c_str());
        break;
    }

    #pragma warning(pop)
}
