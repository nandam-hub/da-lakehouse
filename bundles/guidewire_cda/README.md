Because Guidewire:
- Has several Guidewire Applications under the broader "Guidewire" namespace (e.g. Claim Center, Contact Manager)
- Has instances of each Guidewire Application, _per `amic_environment`_ (e.g. `deva`, `qas`, `prod`)

Our Guidewire CDA data is organized in S3 as follows


```
.
├── s3://amic-lh-dev-raw-catalog/
│   └── guidewire/
│       ├── deva/
│       │   ├── billingcenter/
│       │   │   └── <table_name>/
│       │   │       └── <year=YYYY>/
│       │   │           └── <month=MM>/
│       │   │               └── <day=DD>/
│       │   │                   └── *.snappy.parquet
│       │   ├── claimcenter/
│       │   │   └── ...
│       │   ├── contactmanager/
│       │   │   └── ...
│       │   └── policycenter/
│       │       └── ...
│       └── devb/
│           └── ...
├── s3://amic-lh-test-raw-catalog/
│   └── guidewire/
│       ├── testa/
│       │   └── ...
│       ├── testb/
│       │   └── ...
│       └── qas/
│           └── ...
└── s3://amic-lh-prod-raw-catalog/
    └── guidewire/
        └── prod/
            └── ...
```

Because of this, it made sense to us[^1] implement all `num_guidewire_apps * num_amic_environments` deployments into a heavily-parameterized, one-size-fits-all Databricks Asset Bundle, at the _Guidewire_ level.


>[!WARNING]
**Note**: This is a meaningful departure from the [Cloud Data Assets Naming Convention in our DDLC](https://amerisurewiki.atlassian.net/wiki/spaces/AI/pages/2045739254/DDLC+-+Data+Engineering+Naming+Conventions#Cloud-Data-Assets-(AWS))


[^1]: in September of 2025, at least
