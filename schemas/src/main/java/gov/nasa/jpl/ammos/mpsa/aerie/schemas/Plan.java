
package gov.nasa.jpl.ammos.mpsa.aerie.schemas;



/**
 * Plan
 * <p>
 * A container used to associate an Adaptation with a collection of Activity Instances
 * 
 */
public class Plan {

    /**
     * The ID of the associated adaptation
     * (Required)
     * 
     */
    private String adaptationId;
    /**
     * When the plan ends. Will be changed to a Unix timestamp.
     * (Required)
     * 
     */
    private String endTimestamp;
    /**
     * ID of the plan. Currently a stringified MongoDB object ID.
     * (Required)
     * 
     */
    private String id;
    /**
     * Name of the plan
     * (Required)
     * 
     */
    private String name;
    /**
     * When the plan ends. Will be changed to a Unix timestamp.
     * (Required)
     * 
     */
    private String startTimestamp;

    /**
     * No args constructor for use in serialization
     * 
     */
    public Plan() {
    }

    /**
     * 
     * @param adaptationId
     * @param name
     * @param id
     * @param endTimestamp
     * @param startTimestamp
     */
    public Plan(String adaptationId, String endTimestamp, String id, String name, String startTimestamp) {
        super();
        this.adaptationId = adaptationId;
        this.endTimestamp = endTimestamp;
        this.id = id;
        this.name = name;
        this.startTimestamp = startTimestamp;
    }

    /**
     * The ID of the associated adaptation
     * (Required)
     * 
     */
    public String getAdaptationId() {
        return adaptationId;
    }

    /**
     * The ID of the associated adaptation
     * (Required)
     * 
     */
    public void setAdaptationId(String adaptationId) {
        this.adaptationId = adaptationId;
    }

    /**
     * When the plan ends. Will be changed to a Unix timestamp.
     * (Required)
     * 
     */
    public String getEndTimestamp() {
        return endTimestamp;
    }

    /**
     * When the plan ends. Will be changed to a Unix timestamp.
     * (Required)
     * 
     */
    public void setEndTimestamp(String endTimestamp) {
        this.endTimestamp = endTimestamp;
    }

    /**
     * ID of the plan. Currently a stringified MongoDB object ID.
     * (Required)
     * 
     */
    public String getId() {
        return id;
    }

    /**
     * ID of the plan. Currently a stringified MongoDB object ID.
     * (Required)
     * 
     */
    public void setId(String id) {
        this.id = id;
    }

    /**
     * Name of the plan
     * (Required)
     * 
     */
    public String getName() {
        return name;
    }

    /**
     * Name of the plan
     * (Required)
     * 
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * When the plan ends. Will be changed to a Unix timestamp.
     * (Required)
     * 
     */
    public String getStartTimestamp() {
        return startTimestamp;
    }

    /**
     * When the plan ends. Will be changed to a Unix timestamp.
     * (Required)
     * 
     */
    public void setStartTimestamp(String startTimestamp) {
        this.startTimestamp = startTimestamp;
    }

}
