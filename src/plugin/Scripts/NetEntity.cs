using System.Collections.Generic;
using UnityEngine;
using Assets.Scripts.Inventory__Items__Pickups.Items;

namespace MegabonkTogether.Scripts
{
    /// <summary>
    /// Replaces MonoMod DynamicData. Stores multiplayer network states directly 
    /// on the GameObject for O(1) retrieval and zero garbage collection overhead.
    /// </summary>
    public class NetData
    {
        public uint? NetId;
        public uint? OwnerId;
        public uint? TargetId;
        public uint? PickupId;
        public bool HasSentAlready;
        public EItemRarity? ItemRarity; 
        public bool? IsGoldenShrine;
        public bool? hasBeenSetByServer;
    }

    public static class NetDataManager
    {
        public static readonly Dictionary<int, NetData> Data = new();
    }

    public class NetEntity : MonoBehaviour
    {
        public NetData Data
        {
            get
            {
                int id = this.gameObject.GetInstanceID();
                if (!NetDataManager.Data.TryGetValue(id, out var data))
                {
                    data = new NetData();
                    NetDataManager.Data[id] = data;
                }
                return data;
            }
        }

        private void OnDestroy()
        {
            if (this.gameObject != null)
            {
                NetDataManager.Data.Remove(this.gameObject.GetInstanceID());
            }
        }
    }

    public static class NetEntityExtensions
    {
        private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<object, NetData> cwt = new();

        public static NetData GetOrAddNetEntity(this GameObject obj)
        {
            if (obj == null) return new NetData();

            var netEntity = obj.GetComponent<NetEntity>();
            if (netEntity == null)
            {
                netEntity = obj.AddComponent<NetEntity>();
            }

            return netEntity.Data;
        }

        public static NetData GetOrAddNetEntity(this Component comp)
        {
            if (comp == null) return new NetData();
            if (comp.gameObject != null)
            {
                return GetOrAddNetEntity(comp.gameObject);
            }
            return cwt.GetOrCreateValue(comp);
        }

        public static NetData GetOrAddNetEntity(this Il2CppInterop.Runtime.InteropTypes.Il2CppObjectBase obj)
        {
            if (obj == null) return new NetData();
            return cwt.GetOrCreateValue(obj);
        }
    }
}