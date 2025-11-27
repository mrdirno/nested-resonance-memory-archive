/**
 *
 * Desc:  Program to load the Flash and boot the FPGA of a BittWare Board
 *
 *  Provided by
 *  -----------
 *  BittWare, Inc.
 *  9 Hills Ave
 *  Concord, NH 03301
 *  Ph: (603) 226 0404 
 *  WWW:  http://www.bittware.com
 *  Email:  support@bittware.com
 *
 * Copyright 2008, BittWare, Inc.
 *
 * License:
 * The user is hereby granted a non-exclusive license to use 
 * and or modify this software provided that it runs on BittWare 
 * hardware. Usage of this software on non-BittWare hardware 
 * without the express written permission of BittWare is strictly 
 * prohibited. 
 *
**/

#include <stdio.h>
#include <stdlib.h>
#include "hil.h"

int load_status(HHil hil, HilStatus* msg, void * user)
{
	//printf("Loading; %s, Percent; %d\r", msg->msg, msg->percent);
	printf("Loading Flash %d%%\r", msg->percent);
	return 0;
}	

int main(int argc, char** argv)
{
	HHil hil;
	HDevice dev;
	HResource fpga, flash;
	int entry_number;

	//verify that we have the correct number of arguments passed in
	if(argc <= 2)
	{
		printf("Error : arguments for device number required:\n%s <device number> <path and filename of fpga load>\n", argv[0]);
		return 1;
	}

	if((hil = hil_init(HILINIT_NO_OPTION)) == NULL)
	{
		printf("Error : could not open system handle\n");
		return 1;
	}

	// Open the device.
	entry_number = strtoul(argv[1], NULL, 10);

	if ((dev = hil_open(hil, entry_number, HILOPEN_NO_OPTION)) == NULL)
	{
		printf("problem opening device %d\n", entry_number);
		hil_exit(hil);
		return 1;
	}

	//retrieve FLASH resource
	flash = hil_get_device_resource(dev, HIL_RESOURCE_FLASH, 0);
	if (!flash)
	{
		printf("Board must have a Flash resource in order to run this example - try mapping the device over USB?\n");
		hil_close(dev);
		hil_exit(hil);
		return 1;
	}

	//retrieve FPGA resource
	fpga = hil_get_device_resource(dev, HIL_RESOURCE_FPGA, 0);
	if(!fpga)
	{
		printf("Board must have an FPGA resource in order to run this example.\n");
		hil_close(dev);
		hil_exit(hil);
		return 1;
	}

	//Set the status callback function
	hil_status_setui(hil, load_status, 0);

	// Load the programming file
	if(hil_load(flash, argv[2], HIL_LOAD) < 0) //if loading RBF, should change this to HIL_LOAD_RBF_COMPRESSED
	{
		printf("Error - problem loading %s to Flash partition 1\n", argv[2]);
		hil_close(dev);
		hil_exit(hil);
		return 1;
	}
	printf("Successfully loaded the Flash with %s\n", argv[2]); 

	//Set boot source to the Flash partition just loaded
	hil_set_resource_value(fpga, HIL_FPGA_BOOT_SOURCE, 1);

	// Reload the FPGA from its boot source
	hil_start(fpga, HIL_START);
	printf("Booting the FPGA from %s in Flash \n", argv[2]);

	//close device and exit cleanly
	hil_close(dev);
	hil_exit(hil);
	return 0;
}
