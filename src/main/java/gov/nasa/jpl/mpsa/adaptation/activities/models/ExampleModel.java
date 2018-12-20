package gov.nasa.jpl.mpsa.adaptation.activities.models;

import gov.nasa.jpl.mpsa.activities.operations.AdaptationModel;
import gov.nasa.jpl.mpsa.resources.Resource;
import gov.nasa.jpl.mpsa.resources.ResourcesContainer;

public class ExampleModel implements AdaptationModel {

    @Override
    public void setup() {
        // DO SOME PREPARATION
        System.out.println("No setup needed in this case");
    }

    @Override
    public void execute() {

        ResourcesContainer myResources = ResourcesContainer.getInstance();
        System.out.println("Starting the effects simulation");

        // GET THE RESOURCE TO MODIFY
        Resource main = myResources.getResourceByName("primaryBattery");

        // SET A NEW VALUE FOR THE RESOURCE
        main.setValue(10);
        System.out.println("I have updated the value of my battery");

    }

}



