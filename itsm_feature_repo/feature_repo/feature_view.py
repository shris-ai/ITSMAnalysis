from feast import Entity, Feature, FeatureView, FileSource, ValueType

incident = Entity(name="incident_id", value_type=ValueType.STRING)

itsm_source = FileSource(
    path="data/ITSM_cleaned.csv",
    event_timestamp_column="Open_Time",
)

itsm_features = FeatureView(
    name="itsm_features",
    entities=["incident_id"],
    ttl=None,
    schema=[
        Feature(name="Handle_Time_hrs", dtype=ValueType.FLOAT),
        Feature(name="CI_Name_enc", dtype=ValueType.INT32),
        Feature(name="CI_Cat_enc", dtype=ValueType.INT32),
        Feature(name="CI_Subcat_enc", dtype=ValueType.INT32),
        Feature(name="Closure_Code_enc", dtype=ValueType.INT32),
        Feature(name="Priority_enc", dtype=ValueType.INT32),
        Feature(name="Impact_enc", dtype=ValueType.INT32),
        Feature(name="Urgency_enc", dtype=ValueType.INT32),
    ],
    online=True,
    source=itsm_source,
)
