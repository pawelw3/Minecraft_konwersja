package com.maciej916.indreb.common.block.impl.machines.recycler;

import com.maciej916.indreb.common.container.IndRebContainer;
import com.maciej916.indreb.common.registries.ModContainers;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

public class ContainerRecycler extends IndRebContainer {
   public ContainerRecycler(int windowId, Inventory inv, FriendlyByteBuf data) {
      this(windowId, inv.f_35978_.m_20193_(), data.m_130135_(), inv, inv.f_35978_);
   }

   public ContainerRecycler(int windowId, Level world, BlockPos pos, Inventory playerInventory, Player player) {
      super(ModContainers.RECYCLER, windowId, world, pos, playerInventory, player);
   }
}
