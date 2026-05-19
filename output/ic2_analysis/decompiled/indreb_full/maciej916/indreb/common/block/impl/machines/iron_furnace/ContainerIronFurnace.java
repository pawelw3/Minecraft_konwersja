package com.maciej916.indreb.common.block.impl.machines.iron_furnace;

import com.maciej916.indreb.common.container.IndRebContainer;
import com.maciej916.indreb.common.registries.ModContainers;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

public class ContainerIronFurnace extends IndRebContainer {
   public ContainerIronFurnace(int windowId, Inventory inv, FriendlyByteBuf data) {
      this(windowId, inv.f_35978_.m_20193_(), data.m_130135_(), inv, inv.f_35978_);
   }

   public ContainerIronFurnace(int windowId, Level world, BlockPos pos, Inventory playerInventory, Player player) {
      super(ModContainers.IRON_FURNACE, windowId, world, pos, playerInventory, player);
   }
}
