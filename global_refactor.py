import os
import re

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Ensure using MegabonkTogether.Scripts; is present if we are modifying the file
    # We will add it after the last using statement if not present.
    def add_using(c):
        if 'using MegabonkTogether.Scripts;' not in c:
            # find last using
            last_using = list(re.finditer(r'^using .*?;', c, re.MULTILINE))
            if last_using:
                pos = last_using[-1].end()
                c = c[:pos] + '\nusing MegabonkTogether.Scripts;' + c[pos:]
        return c

    # DynamicData.For(A).Set("B", C) -> A.GetOrAddNetEntity().B = C
    def replace_set(match):
        a = match.group(1)
        b = match.group(2)
        c = match.group(3)
        if b == "netplayId": b = "NetId"
        elif b == "targetId": b = "TargetId"
        elif b == "ownerId": b = "OwnerId"
        elif b == "pickupId": b = "PickupId"
        elif b == "hasSentAlready": b = "HasSentAlready"
        elif b == "rarity": b = "ItemRarity"
        return f"{a}.GetOrAddNetEntity().{b} = {c}"

    content = re.sub(r'(?:MonoMod\.Utils\.)?DynamicData\.For\((.*?)\)\.Set\("([^"]+)",\s*(.*?)\)', replace_set, content)

    # DynamicData.For(A).Get<T>("B") -> A.GetOrAddNetEntity().B
    def replace_get(match):
        a = match.group(1)
        b = match.group(3)
        if b == "netplayId": b = "NetId"
        elif b == "targetId": b = "TargetId"
        elif b == "ownerId": b = "OwnerId"
        elif b == "pickupId": b = "PickupId"
        elif b == "hasSentAlready": b = "HasSentAlready"
        elif b == "rarity": b = "ItemRarity"
        return f"{a}.GetOrAddNetEntity().{b}"

    content = re.sub(r'(?:MonoMod\.Utils\.)?DynamicData\.For\((.*?)\)\.Get<([^>]+)>\("([^"]+)"\)', replace_get, content)
    
    # Also handle some generic `MonoMod.Utils.DynamicData.For(...)`
    
    # 3. DynamicData.For(A).Data.Clear() -> var netEnt = A.GetComponent<NetEntity>(); if (netEnt != null) UnityEngine.Object.Destroy(netEnt);
    def replace_clear(match):
        a = match.group(1)
        return f"var netEnt = {a}.GetComponent<NetEntity>(); if (netEnt != null) UnityEngine.Object.Destroy(netEnt)"
    content = re.sub(r'(?:MonoMod\.Utils\.)?DynamicData\.For\((.*?)\)\.Data\.Clear\(\)', replace_clear, content)

    # Clean up local dyn variables if they exist
    # e.g., var dynPickup = DynamicData.For(__instance);
    # Actually, the python regex might not catch things like dynPickup.Get...
    # We should catch them by simple string replacement.
    local_dyns = re.findall(r'var\s+(\w+)\s*=\s*(?:MonoMod\.Utils\.)?DynamicData\.For\((.*?)\);', content)
    for var_name, var_target in local_dyns:
        # replace the declaration with empty or comment
        content = re.sub(r'var\s+' + var_name + r'\s*=\s*(?:MonoMod\.Utils\.)?DynamicData\.For\(' + re.escape(var_target) + r'\);', '', content)
        # replace dynPickup.Set
        content = re.sub(var_name + r'\.Set\("([^"]+)",\s*(.*?)\)', lambda m: f"{var_target}.GetOrAddNetEntity().{m.group(1).replace('netplayId', 'NetId').replace('ownerId','OwnerId').replace('targetId','TargetId').replace('rarity','ItemRarity')} = {m.group(2)}", content)
        # replace dynPickup.Get<T>("B")
        content = re.sub(var_name + r'\.Get<([^>]+)>\("([^"]+)"\)', lambda m: f"{var_target}.GetOrAddNetEntity().{m.group(2).replace('netplayId', 'NetId').replace('ownerId','OwnerId').replace('targetId','TargetId').replace('rarity','ItemRarity')}", content)
        # replace dynPickup.Data.Clear()
        content = re.sub(var_name + r'\.Data\.Clear\(\)', lambda m: f"var netEnt = {var_target}.GetComponent<NetEntity>(); if (netEnt != null) UnityEngine.Object.Destroy(netEnt)", content)

    # remove MonoMod.Utils using if present
    content = content.replace('using MonoMod.Utils;', '')

    if content != original_content:
        content = add_using(content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

modified = []
for root, dirs, files in os.walk('src/plugin'):
    for file in files:
        if file.endswith('.cs') and file != 'SynchronizationService.cs':
            path = os.path.join(root, file)
            if process_file(path):
                modified.append(path)

print(f"Refactored {len(modified)} files.")
