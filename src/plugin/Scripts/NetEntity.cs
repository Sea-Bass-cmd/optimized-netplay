using UnityEngine;
using Assets.Scripts.Inventory__Items__Pickups.Items;

namespace MegabonkTogether.Scripts
{
    /// <summary>
    /// Replaces MonoMod DynamicData. Stores multiplayer network states directly 
    /// on the GameObject for O(1) retrieval and zero garbage collection overhead.
    /// </summary>
    public class NetEntity : MonoBehaviour
    {
        public uint? NetId;
        public uint? OwnerId;
        public uint? TargetId;
        public uint? PickupId;
        public bool HasSentAlready;
        public EItemRarity? ItemRarity; 
    }

    public static class NetEntityExtensions
    {
        public static NetEntity GetOrAddNetEntity(this GameObject obj)
        {
            if (obj == null) return null;
            var netEntity = obj.GetComponent<NetEntity>();
            if (netEntity == null) netEntity = obj.AddComponent<NetEntity>();
            return netEntity;
        }

        public static NetEntity GetOrAddNetEntity(this Component comp)
        {
            if (comp == null || comp.gameObject == null) return null;
            return GetOrAddNetEntity(comp.gameObject);
        }
    }
}