import re
import os

def fix_concurrency(file_path, var_name, dict_name):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Change type to int and remove TODO
    content = re.sub(r'private uint ' + var_name + r' = 0;\s*//TODO: concurrency\?', f'private int {var_name} = 0;', content)
    
    # Replace ++ with Interlocked
    # Before:
    # currentEnemyId++;
    # if (!spawnedEnemies.TryAdd(currentEnemyId, enemy))
    # {
    #     Plugin.Log.LogWarning($"Attempted to add an enemy that already exists. EnemyId: {currentEnemyId}");
    # }
    # return currentEnemyId;
    
    # We will use regex to find the block
    pattern = r'' + var_name + r'\+\+;\s*if \(!' + dict_name + r'\.TryAdd\(' + var_name + r', (.*?)\)\)\s*\{([^}]*)\}\s*return ' + var_name + r';'
    
    def replacer(m):
        obj_name = m.group(1)
        warning_body = m.group(2).replace(var_name, 'newId')
        return f"""var newId = (uint)System.Threading.Interlocked.Increment(ref {var_name});
            if (!{dict_name}.TryAdd(newId, {obj_name}))
            {{{warning_body}}}
            return newId;"""
            
    content = re.sub(pattern, replacer, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

fix_concurrency('src/plugin/Services/EnemyManagerService.cs', 'currentEnemyId', 'spawnedEnemies')
fix_concurrency('src/plugin/Services/PickupManagerService.cs', 'currentPickupId', 'spawnedPickups')
fix_concurrency('src/plugin/Services/SpawnedObjectManagerService.cs', 'currentObjectId', 'spawnedObjects')
