using Assets.Scripts.Inventory__Items__Pickups.Weapons;
using Assets.Scripts.Inventory__Items__Pickups.Weapons.Attacks;
using Assets.Scripts.Objects.Pooling;
using HarmonyLib;
using MegabonkTogether.Services;
using Microsoft.Extensions.DependencyInjection;
using MegabonkTogether.Scripts;


namespace MegabonkTogether.Patches
{
    [HarmonyPatch(typeof(PoolManager))]
    internal class PoolManagerPatches
    {
        private static readonly ISynchronizationService synchronizationService = Plugin.Services.GetService<ISynchronizationService>();

        /// <summary>
        /// Set the ownerId on the WeaponAttack when it's retrieved from the pool (for remote players' attacks)
        /// </summary>
        [HarmonyPostfix]
        [HarmonyPatch(nameof(PoolManager.GetAttack))]
        public static void GetAttack_Postfix(ref WeaponAttack __result, WeaponBase weaponBase)
        {
            if (!synchronizationService.HasNetplaySessionStarted())
            {
                return;
            }

            
            var ownerId = NetData.Get(weaponBase).OwnerId;

            if (ownerId.HasValue)
            {
                NetData.Get(__result).OwnerId = ownerId.Value;
            }
        }
    }
}