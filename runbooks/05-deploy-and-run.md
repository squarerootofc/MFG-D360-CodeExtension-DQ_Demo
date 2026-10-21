[← Guide index](../README.md)

# 5. Deploy and run

A deployed code extension **doesn't run on its own**. You deploy it, then run it
through a **batch data transform** created with *Create From Code Extension*.

## Step 5.1: Deploy (10–20 min, mostly waiting)

**Option A: CLI.** Docker must be running. Run this from the package root (`~/dev/abt_contact_dq`):

```bash
sf data-code-extension script deploy \
  --target-org abt-demo \
  --name ABT_Contact_DQ \
  --package-version 1.0.0 \
  --description "ABT contact DQ: email / phone / country + DQ hash" \
  --cpu-size CPU_L \
  --package-dir ./payload
```

- `--package-dir` must point at `./payload`, **not** the project root.
- If you leave out `--cpu-size`, it defaults to **CPU_2XL** (16 CU/hr). For anything under about a million rows, use **CPU_L** (4 CU/hr).

**Option B: UI upload.** Use this if Docker is blocked.

1. Zip the package: `sf data-code-extension script zip --package-dir ./payload` (it must be under 5 GB).
2. In **Data Cloud Setup**, go to **Developer Tools**, then **Code Extension**, and click **New**. Enter:
   - Deployment Name: `ABT Contact DQ`
   - API Name: `ABT_Contact_DQ`
   - Description
3. On the next screen, set:

   | Setting | Value |
   |---------|-------|
   | Language | **Python** |
   | Code Type | **Script** |
   | Use in Feature | **Batch Data Transform** |
   | Compute Size | **Standard - Large** (4 CU/hr) |

4. Upload the zip and click **Submit Code**.

**Check:** go to **Code Extension**, then **ABT_Contact_DQ**, then the **Details** tab. Deployment Status should be **Deployed**.

## Step 5.2: Create the batch data transform (5 min)

1. In the Data Cloud app, go to **Data Transforms**, click **New**, choose **Create From Code Extension**, and click **Next**.
2. Name it `ABT Contact DQ Run`, with API name `ABT_Contact_DQ_Run`. Select **ABT_Contact_DQ** and save.
3. The transform's detail page should show the source as *Code Extension*, with `ABT_Contact_Raw__dll` as input and `ABT_Contact_DQ__dll` as output.

## Step 5.3: Run it

Click **Run Now**. **Don't schedule it yet.** Scheduling comes after the output has been verified ([section 6](06-verify-and-iterate.md)).

## Step 5.4: Watch Run History

Go to **Data Cloud Setup**, then **Code Extension**, then **ABT_Contact_DQ**, then **Run History**:

| Column | Expected |
|--------|----------|
| Status | **Succeeded** |
| Rows read | **30,000** |
| Rows written | **30,000** |
| Runtime (click **Submitted Date**) | Not yet measured: record it. **Runtime is what you're billed for** (60-second minimum) |

## ✅ Exit check for section 5

- [ ] Deployment Status shows **Deployed**
- [ ] The batch data transform `ABT_Contact_DQ_Run` exists, with *Code Extension* as its source
- [ ] The first run **Succeeded**, with 30,000 rows read and 30,000 written

---

[← 4. Build and test locally](04-build-and-test-locally.md) · [Guide index](../README.md) · **Next: [6. Verify and iterate →](06-verify-and-iterate.md)**
