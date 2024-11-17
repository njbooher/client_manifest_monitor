# Steam Client Manifest Monitor

Monitors the [client manifests](/resources/client_manifest_urls.txt) on the CDN for symbols and other leaks. Updates run hourly at the :45 mark. 

For each manifest, all contained zip files are downloaded and the contents listed, and this is concatenated and deduped in [/results/manifest_files](/results/manifest_files).

The aggregate list of zips across all manifests is in [/results/client_manifest_filenames_clean.txt](/results/client_manifest_filenames_clean.txt)

If you know of any manifests that are missing from the list, please let me know.
