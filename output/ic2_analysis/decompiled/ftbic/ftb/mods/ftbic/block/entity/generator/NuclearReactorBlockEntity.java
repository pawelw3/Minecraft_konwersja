package dev.ftb.mods.ftbic.block.entity.generator;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.FTBICBlocks;
import dev.ftb.mods.ftbic.block.FTBICElectricBlocks;
import dev.ftb.mods.ftbic.block.NuclearReactorChamberBlock;
import dev.ftb.mods.ftbic.item.reactor.NuclearReactor;
import dev.ftb.mods.ftbic.item.reactor.ReactorItem;
import dev.ftb.mods.ftbic.screen.NuclearReactorMenu;
import dev.ftb.mods.ftbic.screen.sync.SyncedData;
import dev.ftb.mods.ftbic.screen.sync.SyncedDataKey;
import dev.ftb.mods.ftbic.sound.FTBICSounds;
import dev.ftb.mods.ftbic.util.FTBICUtils;
import dev.ftb.mods.ftbic.util.NuclearExplosion;
import it.unimi.dsi.fastutil.bytes.Byte2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.bytes.ByteArrayList;
import it.unimi.dsi.fastutil.bytes.Byte2ObjectMap.Entry;
import it.unimi.dsi.fastutil.objects.ObjectIterator;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Random;
import net.minecraft.ChatFormatting;
import net.minecraft.Util;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.ChatType;
import net.minecraft.network.chat.TextComponent;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.registries.ForgeRegistries;
import org.jetbrains.annotations.NotNull;

public class NuclearReactorBlockEntity extends GeneratorBlockEntity {
   public static final int[] OFFSET_X = new int[]{0, 0, -1, 1};
   public static final int[] OFFSET_Y = new int[]{-1, 1, 0, 0};
   public static final SyncedDataKey<Double> ENERGY_OUTPUT = new SyncedDataKey("energy_output", 0.0);
   public double ENERGY_MULTIPLIER = (Double)FTBICConfig.MACHINES.NUCLEAR_GENERATOR_OUTPUT.get();
   public static final SyncedDataKey<Integer> HEAT = new SyncedDataKey("heat", 0);
   public static final SyncedDataKey<Integer> MAX_HEAT = new SyncedDataKey("max_heat", 0);
   public int timeUntilNextCycle;
   public final NuclearReactor reactor;
   public int debugSpeed = 0;
   public Byte2ObjectOpenHashMap<Item> plan;

   public NuclearReactorBlockEntity(BlockPos pos, BlockState state) {
      super(FTBICElectricBlocks.NUCLEAR_REACTOR, pos, state);
      this.reactor = new NuclearReactor(this.inputItems);
   }

   @Override
   public void initProperties() {
      super.initProperties();
      this.maxEnergyOutputTransfer = (Double)FTBICConfig.ENERGY.IV_TRANSFER_RATE.get();
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);
      tag.m_128405_("TimeUntilNextCycle", this.timeUntilNextCycle);
      tag.m_128379_("Paused", this.reactor.paused);
      tag.m_128379_("AllowRedstoneControl", this.reactor.allowRedstoneControl);
      tag.m_128347_("EnergyOutput", this.reactor.energyOutput);
      tag.m_128405_("Heat", this.reactor.heat);
      if (this.debugSpeed > 0) {
         tag.m_128405_("DebugSpeed", this.debugSpeed);
      }

      if (this.plan != null && !this.plan.isEmpty()) {
         HashMap<Item, ByteArrayList> pmap = new HashMap<>();
         ObjectIterator ptag = this.plan.byte2ObjectEntrySet().iterator();

         while (ptag.hasNext()) {
            Entry<Item> entry = (Entry<Item>)ptag.next();
            pmap.computeIfAbsent((Item)entry.getValue(), k -> new ByteArrayList()).add(entry.getByteKey());
         }

         CompoundTag ptagx = new CompoundTag();

         for (java.util.Map.Entry<Item, ByteArrayList> entry : pmap.entrySet()) {
            ptagx.m_128382_(entry.getKey().getRegistryName().toString(), entry.getValue().toByteArray());
         }

         tag.m_128365_("Plan", ptagx);
      }
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      this.timeUntilNextCycle = tag.m_128451_("TimeUntilNextCycle");
      this.reactor.paused = tag.m_128471_("Paused");
      this.reactor.allowRedstoneControl = tag.m_128471_("AllowRedstoneControl");
      this.reactor.energyOutput = tag.m_128459_("EnergyOutput");
      this.reactor.heat = tag.m_128451_("Heat");
      this.debugSpeed = tag.m_128451_("DebugSpeed");
      CompoundTag ptag = tag.m_128469_("Plan");
      if (!ptag.m_128456_()) {
         this.plan = new Byte2ObjectOpenHashMap();

         for (String s : ptag.m_128431_()) {
            Item item = (Item)ForgeRegistries.ITEMS.getValue(new ResourceLocation(s));
            if (item instanceof ReactorItem) {
               for (byte b : ptag.m_128463_(s)) {
                  this.plan.put(b, item);
               }
            }
         }

         if (this.plan.isEmpty()) {
            this.plan = null;
         }
      } else {
         this.plan = null;
      }
   }

   @Override
   public int getSlotLimit(int slot) {
      return 1;
   }

   @Override
   public boolean isItemValid(int slot, @NotNull ItemStack stack) {
      return stack.m_41720_() instanceof ReactorItem && (this.plan == null || this.plan.get((byte)slot) == stack.m_41720_());
   }

   @Override
   public boolean savePlacer() {
      return true;
   }

   @Override
   public void addSyncData(SyncedData data) {
      super.addSyncData(data);
      data.addBoolean(SyncedData.PAUSED, () -> this.reactor.paused);
      data.addBoolean(SyncedData.ALLOW_REDSTONE_CONTROL, () -> this.reactor.allowRedstoneControl);
      data.addDouble(ENERGY_OUTPUT, () -> this.reactor.energyOutput * this.ENERGY_MULTIPLIER);
      data.addInt(HEAT, () -> this.reactor.heat);
      data.addInt(MAX_HEAT, () -> this.reactor.maxHeat);
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_()) {
         this.openMenu((ServerPlayer)player, (id, inventory) -> new NuclearReactorMenu(id, inventory, this));
      }

      return InteractionResult.SUCCESS;
   }

   private void checkPoweredState(Level level, BlockPos pos, BlockState state) {
      if (this.reactor.allowRedstoneControl) {
         this.reactor.paused = !level.m_46753_(pos);
      }
   }

   @Override
   public void handleGeneration() {
      this.timeUntilNextCycle--;
      if (this.timeUntilNextCycle <= 0) {
         this.timeUntilNextCycle = 20;
         if (this.debugSpeed <= 0) {
            this.handleReactor();
         }
      }

      if (this.debugSpeed > 0) {
         for (int i = 0; i < this.debugSpeed; i++) {
            this.handleReactor();
         }
      }

      if (this.reactor.energyOutput > 0.0) {
         this.active = true;
         this.energy = this.energy + Math.min(this.reactor.energyOutput, this.energyCapacity - this.energy);
         this.energy = this.energy * this.ENERGY_MULTIPLIER;
      }

      if (this.f_58857_ != null) {
         this.checkPoweredState(this.f_58857_, this.f_58858_, this.m_58900_());
      }

      if (this.f_58857_ != null && !this.f_58857_.m_5776_() && this.reactor.heat > 0 && this.reactor.maxHeat > 0) {
         float h = (float)this.reactor.heat / (float)this.reactor.maxHeat;
         if (h >= 1.0F) {
            if (this.debugSpeed > 0) {
               this.f_58857_
                  .m_142572_()
                  .m_6846_()
                  .m_11264_(
                     new TextComponent(
                        String.format(
                           "Debug Nuclear Reactor at %d, %d, %d exploded:", this.f_58858_.m_123341_(), this.f_58858_.m_123342_(), this.f_58858_.m_123343_()
                        )
                     ),
                     ChatType.SYSTEM,
                     Util.f_137441_
                  );
               this.f_58857_
                  .m_142572_()
                  .m_6846_()
                  .m_11264_(new TextComponent(String.format("- Radius: %,d", Mth.m_14165_(this.reactor.explosionRadius))), ChatType.SYSTEM, Util.f_137441_);
               this.f_58857_
                  .m_142572_()
                  .m_6846_()
                  .m_11264_(
                     new TextComponent(
                        String.format(
                           "- Heat: %s / %s \ud83d\udd25",
                           FTBICUtils.formatEnergyValue((double)this.reactor.heat),
                           FTBICUtils.formatEnergyValue((double)this.reactor.maxHeat)
                        )
                     ),
                     ChatType.SYSTEM,
                     Util.f_137441_
                  );
               this.f_58857_
                  .m_142572_()
                  .m_6846_()
                  .m_11264_(
                     new TextComponent(String.format("- Energy: %s/t", FTBICUtils.formatEnergyValue(this.reactor.energyOutput))),
                     ChatType.SYSTEM,
                     Util.f_137441_
                  );
               this.reactor.paused = true;
               this.reactor.heat = this.reactor.maxHeat - 1;
               this.m_6596_();
            } else {
               Arrays.fill(this.inputItems, ItemStack.f_41583_);
               this.m_6596_();
               this.f_58857_.m_7731_(this.f_58858_, ((Block)FTBICBlocks.ACTIVE_NUKE.get()).m_49966_(), 3);

               for (Direction direction : FTBICUtils.DIRECTIONS) {
                  if (this.f_58857_.m_8055_(this.f_58858_.m_142300_(direction)).m_60734_() instanceof NuclearReactorChamberBlock) {
                     this.f_58857_.m_7731_(this.f_58858_.m_142300_(direction), ((Block)FTBICBlocks.ACTIVE_NUKE.get()).m_49966_(), 3);
                  }
               }

               NuclearExplosion.builder((ServerLevel)this.f_58857_, this.f_58858_, this.reactor.explosionRadius, this.placerId, this.placerName)
                  .preExplosion(
                     () -> {
                        this.f_58857_
                           .m_142572_()
                           .m_6846_()
                           .m_11264_(
                              new TranslatableComponent("block.ftbic.nuclear_reactor.broadcast", new Object[]{this.placerName}),
                              ChatType.SYSTEM,
                              Util.f_137441_
                           );
                        Player player = this.f_58857_.m_142572_().m_6846_().m_11259_(this.placerId);
                        if (player != null) {
                           player.m_6352_(
                              new TextComponent(
                                    String.format(
                                       "%s : [%d, %d, %d]",
                                       this.f_58857_.m_46472_().m_135782_(),
                                       this.f_58858_.m_123341_(),
                                       this.f_58858_.m_123342_(),
                                       this.f_58858_.m_123343_()
                                    )
                                 )
                                 .m_130940_(ChatFormatting.GRAY),
                              Util.f_137441_
                           );
                        }

                        this.f_58857_.m_7471_(this.f_58858_, false);
                     }
                  )
                  .create();
            }
         } else if (h >= 0.75F && this.f_58857_.m_46467_() % 25L == 0L && this.reactor.energyOutput > 0.0) {
            this.f_58857_.m_5594_(null, this.f_58858_, (SoundEvent)FTBICSounds.RADIATION.get(), SoundSource.BLOCKS, 0.5F, 1.0F);
         }
      }
   }

   public void handleReactor() {
      if (this.f_58857_ != null && !this.f_58857_.m_5776_()) {
         double peo = this.reactor.energyOutput;
         int ph = this.reactor.heat;
         this.reactor.tick();
         if (peo != this.reactor.energyOutput || ph != this.reactor.heat) {
            this.m_6596_();
         }
      }
   }

   @Override
   public void onBroken(Level level, BlockPos pos) {
      if (this.debugSpeed <= 0) {
         super.onBroken(level, pos);
      }
   }

   @OnlyIn(Dist.CLIENT)
   @Override
   public void spawnActiveParticles(Level level, double x, double y, double z, BlockState state, Random r) {
   }
}
